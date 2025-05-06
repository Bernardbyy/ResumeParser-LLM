# matcher.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ResumeMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        
    def calculate_match(self, resume_data, job_data):
        """Main entry point for matching"""
        scores = {
            'technical_skills': self.match_technical_skills(resume_data, job_data),
            'domain_knowledge': self.match_domain_knowledge(resume_data, job_data),
            'experience': self.match_experience(resume_data, job_data),
            'soft_skills': self.match_soft_skills(resume_data, job_data),
            'responsibilities': self.match_responsibilities(resume_data, job_data)
        }
        
        # Calculate weighted overall score
        weights = {
            'technical_skills': 0.30,
            'domain_knowledge': 0.25,
            'experience': 0.20,
            'soft_skills': 0.10,
            'responsibilities': 0.15
        }
        
        overall_score = sum(scores[key]['score'] * weights[key] for key in weights)
        
        return {
            'overall_score': overall_score,
            'category_scores': scores,
            'weights': weights
        }
    
    def keyword_match(self, job_items, resume_items):
        """Exact matching for standardized terms"""
        if not job_items or not resume_items:
            return [], 0.0
        
        # Normalize to lowercase for comparison
        job_items_lower = [item.lower() for item in job_items]
        resume_items_lower = [item.lower() for item in resume_items]
        
        matches = []
        for i, job_item in enumerate(job_items):
            if job_items_lower[i] in resume_items_lower:
                matches.append(job_item)
        
        score = len(matches) / len(job_items) if job_items else 0.0
        return matches, score
    
    def semantic_match(self, job_items, resume_texts, threshold=0.3):
        """Semantic matching using TF-IDF and cosine similarity"""
        if not job_items or not resume_texts:
            return [], 0.0
        
        # Ensure resume_texts is a list
        if isinstance(resume_texts, str):
            resume_texts = [resume_texts]
        
        # Filter out empty texts
        resume_texts = [text for text in resume_texts if text.strip()]
        
        if not resume_texts:
            return [], 0.0
        
        # Combine all texts
        all_texts = job_items + resume_texts
        
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Split matrices
            job_vectors = tfidf_matrix[:len(job_items)]
            resume_vectors = tfidf_matrix[len(job_items):]
            
            # Calculate similarities
            similarity_matrix = cosine_similarity(job_vectors, resume_vectors)
            
            # Find matches above threshold
            matches = []
            for i, job_item in enumerate(job_items):
                max_similarity = similarity_matrix[i].max()
                if max_similarity >= threshold:
                    matches.append({
                        'item': job_item,
                        'similarity': max_similarity
                    })
            
            score = len(matches) / len(job_items) if job_items else 0.0
            return matches, score
            
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return [], 0.0
    
    def match_technical_skills(self, resume_data, job_data):
        """Match technical skills using appropriate techniques"""
        resume_tech = resume_data.get('skills', {}).get('technical', {})
        job_tech = job_data.get('technical_skills', {})
        
        matches = {}
        scores = []
        
        # Keyword matching for specific categories
        for category in ['languages', 'frameworks', 'tools', 'databases', 'cloud']:
            job_items = job_tech.get(category, [])
            resume_items = resume_tech.get(category, [])
            
            category_matches, category_score = self.keyword_match(job_items, resume_items)
            matches[category] = category_matches
            if job_items:  # Only include in scoring if job has requirements
                scores.append(category_score)
        
        # Semantic matching for general requirements
        job_required = job_tech.get('required', [])
        if job_required:
            # Combine all resume technical skills
            all_resume_tech = []
            for category in ['languages', 'frameworks', 'tools', 'databases', 'cloud']:
                all_resume_tech.extend(resume_tech.get(category, []))
            
            # Also check in job responsibilities
            responsibilities_text = self.extract_responsibilities_text(resume_data)
            
            semantic_matches, semantic_score = self.semantic_match(
                job_required, 
                all_resume_tech + [responsibilities_text]
            )
            
            matches['required'] = semantic_matches
            scores.append(semantic_score)
        
        # Calculate overall technical skills score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            'score': overall_score,
            'matches': matches,
            'details': f"Matched {sum(len(m) if isinstance(m, list) else len(m) for m in matches.values() if m)} technical skills"
        }
    
    def match_domain_knowledge(self, resume_data, job_data):
        """Match domain knowledge requirements"""
        job_domains = job_data.get('domain_knowledge', {}).get('required', [])
        
        # Extract relevant resume text
        resume_text = self.extract_all_text_for_semantic(
            resume_data, 
            ['skills.domain', 'experience.responsibilities', 'education.field']
        )
        
        matches, score = self.semantic_match(job_domains, [resume_text])
        
        return {
            'score': score,
            'matches': matches,
            'details': f"Matched {len(matches)} domain areas"
        }
    
    def match_experience_years(self, job_years, resume_years):
        """Match years of experience"""
        if job_years is None or job_years == 0:
            return 1.0  # No requirement
        
        if resume_years >= job_years:
            return 1.0
        else:
            # Partial credit - closer to requirement gets higher score
            return max(0.0, min(1.0, resume_years / job_years))
    
    def match_education_requirements(self, job_education_reqs, resume_education):
        """Special matching for education requirements"""
        if not job_education_reqs or not resume_education:
            return [], 1.0  # If no requirements, perfect match
        
        degree_patterns = {
            'phd': r'ph\.?d|doctorate|doctoral',
            'master': r'master|m\.?s\.?|m\.?sc\.?|m\.?a\.?|mba',
            'bachelor': r'bachelor|b\.?s\.?|b\.?sc\.?|b\.?a\.?|b\.?eng\.?'
        }
        
        matches = []
        for job_req in job_education_reqs:
            job_req_lower = job_req.lower()
            
            # Check each resume education entry
            for edu in resume_education:
                edu_text = f"{edu.get('degree', '')} {edu.get('field', '')}".lower()
                
                # Check for degree level matches
                for degree_level, pattern in degree_patterns.items():
                    if re.search(pattern, job_req_lower) and re.search(pattern, edu_text):
                        matches.append({
                            'requirement': job_req,
                            'matched': f"{edu.get('degree')} in {edu.get('field')}",
                            'level': degree_level
                        })
                        break
                
                # Also check for field matches
                if any(field in edu_text for field in job_req_lower.split()):
                    if not any(m['requirement'] == job_req for m in matches):
                        matches.append({
                            'requirement': job_req,
                            'matched': f"{edu.get('degree')} in {edu.get('field')}",
                            'level': 'field_match'
                        })
        
        score = len(matches) / len(job_education_reqs) if job_education_reqs else 1.0
        return matches, score
    
    def match_experience(self, resume_data, job_data):
        """Match experience requirements"""
        job_exp = job_data.get('experience_requirements', {})
        resume_exp = resume_data.get('experience', {})
        
        scores = []
        matches = {}
        
        # Years of experience
        job_years = job_exp.get('minimum_years', 0)
        resume_years = resume_exp.get('total_years', 0)
        years_score = self.match_experience_years(job_years, resume_years)
        scores.append(years_score)
        matches['years'] = {'required': job_years, 'actual': resume_years, 'score': years_score}
        
        # Education requirements
        job_education = job_exp.get('required_education', [])
        resume_education = resume_data.get('education', [])
        edu_matches, edu_score = self.match_education_requirements(job_education, resume_education)
        if job_education:  # Only include in scoring if there are requirements
            scores.append(edu_score)
        matches['education'] = edu_matches
        
        # Specific experience
        specific_exp = job_exp.get('specific_experience', [])
        if specific_exp:
            responsibilities_text = self.extract_responsibilities_text(resume_data)
            position_titles = [pos.get('title', '') for pos in resume_exp.get('positions', [])]
            combined_text = responsibilities_text + ' ' + ' '.join(position_titles)
            
            exp_matches, exp_score = self.semantic_match(specific_exp, [combined_text])
            scores.append(exp_score)
            matches['specific'] = exp_matches
        
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            'score': overall_score,
            'matches': matches,
            'details': f"Experience match: {overall_score:.0%}"
        }
    
    def match_soft_skills(self, resume_data, job_data):
        """Match soft skills requirements"""
        job_soft_skills = job_data.get('soft_skills', {}).get('required', [])
        
        # Extract relevant resume text
        resume_text = self.extract_all_text_for_semantic(
            resume_data,
            ['skills.soft', 'miscellaneous', 'experience.responsibilities']
        )
        
        matches, score = self.semantic_match(job_soft_skills, [resume_text])
        
        return {
            'score': score,
            'matches': matches,
            'details': f"Matched {len(matches)} soft skills"
        }
    
    def match_responsibilities(self, resume_data, job_data):
        """Match job responsibilities"""
        job_responsibilities = job_data.get('job_responsibilities', {})
        
        # Extract all responsibilities and titles from resume
        responsibilities_text = self.extract_responsibilities_text(resume_data)
        position_titles = [pos.get('title', '') for pos in resume_data.get('experience', {}).get('positions', [])]
        combined_text = responsibilities_text + ' ' + ' '.join(position_titles)
        
        matches = {}
        scores = []
        
        # Match primary responsibilities
        primary_resp = job_responsibilities.get('primary', [])
        if primary_resp:
            primary_matches, primary_score = self.semantic_match(primary_resp, [combined_text])
            matches['primary'] = primary_matches
            scores.append(primary_score)
        
        # Match secondary responsibilities (with lower weight)
        secondary_resp = job_responsibilities.get('secondary', [])
        if secondary_resp:
            secondary_matches, secondary_score = self.semantic_match(secondary_resp, [combined_text])
            matches['secondary'] = secondary_matches
            scores.append(secondary_score * 0.5)  # Give less weight to secondary
        
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            'score': overall_score,
            'matches': matches,
            'details': f"Matched responsibilities: {overall_score:.0%}"
        }
    
    def extract_responsibilities_text(self, resume_data):
        """Extract all responsibilities as a single text"""
        responsibilities = []
        for position in resume_data.get('experience', {}).get('positions', []):
            responsibilities.extend(position.get('responsibilities', []))
        return ' '.join(responsibilities)
    
    def extract_all_text_for_semantic(self, resume_data, fields):
        """Extract text from multiple resume fields for semantic matching"""
        texts = []
        
        # Add specific fields
        if 'skills.domain' in fields:
            texts.extend(resume_data.get('skills', {}).get('domain', []))
        
        if 'skills.soft' in fields:
            texts.extend(resume_data.get('skills', {}).get('soft', []))
        
        if 'experience.responsibilities' in fields:
            texts.append(self.extract_responsibilities_text(resume_data))
        
        if 'education.field' in fields:
            for edu in resume_data.get('education', []):
                texts.append(edu.get('field', ''))
        
        if 'miscellaneous' in fields:
            texts.extend(resume_data.get('miscellaneous', []))
        
        return ' '.join(filter(None, texts))  # Filter out None or empty strings