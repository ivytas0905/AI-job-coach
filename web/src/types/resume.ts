// Type definitions for Resume system

export interface PersonalInfo {
  name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
}

export interface BulletPoint {
  id?: string;
  text: string;
  keywords?: string[];
  skills_used?: string[];
}

export interface Experience {
  id?: string;
  company?: string;
  title?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  bullets: BulletPoint[];
  skills_used?: string[];
  industry?: string;
}

export interface Education {
  id?: string;
  school?: string;
  degree?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

export interface Skill {
  name: string;
  category?: string;
}

export interface MasterResume {
  id?: string;
  user_id?: string;
  personal_info?: PersonalInfo;
  experiences: Experience[];
  education: Education[];
  skills: Skill[];
  created_at?: string;
  updated_at?: string;
}

export interface KeywordWeight {
  text: string;
  weight: number;
  category: string;
}

// Enhanced API types (new endpoints)
export interface KeywordItem {
  keyword: string;
  weight: number;
  type: 'technical_skill' | 'soft_skill' | 'tool' | 'certification' | 'domain_knowledge';
}

export interface JobRequirements {
  education: string[];
  experience_years: number | null;
  responsibilities: string[];
}

export interface AnalysisMetadata {
  analyzed_at: string;
  cache_hit: boolean;
}

export interface JDSections {
  summary?: string;
  description?: string;
  responsibilities?: string[];
  minimum_qualifications?: string[];
  preferred_qualifications?: string[];
  benefits?: string[];
}

export interface EnhancedJobDescription {
  jd_id: string;
  sections?: JDSections;
  top_keywords: KeywordItem[];
  required_skills: string[];
  preferred_skills: string[];
  job_requirements: JobRequirements;
  analysis_metadata: AnalysisMetadata;
  cached: boolean;
}

// Legacy JobDescription type (keep for backward compatibility)
export interface JobDescription {
  id?: string;
  raw_text: string;
  company?: string;
  position?: string;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  qualifications: string[];
  industry?: string;
  keywords: KeywordWeight[];
  analyzed_at?: string;
}

export interface BulletOptimization {
  bullet_id: string;
  original_text: string;
  optimized_text: string;
  improvements: string[];
  keyword_matches: string[];
  status: 'pending' | 'accepted' | 'rejected';
}

export interface TailoredResume {
  id?: string;
  master_resume_id: string;
  jd_id: string;
  selected_experience_ids: string[];
  selected_bullet_optimizations: BulletOptimization[];
  selected_education_ids: string[];
  selected_skills: string[];
  match_score: number;
  ats_score: number;
  created_at?: string;
}
