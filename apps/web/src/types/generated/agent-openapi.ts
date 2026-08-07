// Generated from agent_service FastAPI OpenAPI. Do not edit by hand.
export interface paths {
    "/api/v1/resume/build/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Build Resume
         * @description Build resume from form data
         *
         *     This endpoint:
         *     1. Receives form data from frontend
         *     2. Converts to domain model
         *     3. Optionally enhances with AI
         *     4. Returns structured data for preview
         *
         *     Note: File generation (PDF/Word) is handled by /api/resume/generate
         */
        post: operations["build_resume_api_v1_resume_build__post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/resume/build/validate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Validate Resume Data
         * @description Validate resume data without building
         *
         *     Useful for real-time validation as user fills the form
         */
        post: operations["validate_resume_data_api_v1_resume_build_validate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/resume/build/preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Generate Preview
         * @description Generate HTML preview of resume
         *
         *     Used for showing preview before download
         *     Returns HTML string that can be rendered in frontend
         */
        post: operations["generate_preview_api_v1_resume_build_preview_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/resume/generate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Generate Resume
         * @description Generate resume file (PDF or Word)
         *
         *     This endpoint is shared by:
         *     - Build Resume workflow (form-based creation)
         *     - Upload Resume workflow (file upload + optimization)
         *
         *     Args:
         *         request: GenerateResumeRequest containing resume data, template, and format
         *
         *     Returns:
         *         File download response (PDF or DOCX)
         */
        post: operations["generate_resume_api_v1_resume_generate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/resume/enhance": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Enhance Content */
        post: operations["enhance_content_api_v1_resume_enhance_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/resume/enhance-summary": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Enhance Summary */
        post: operations["enhance_summary_api_v1_resume_enhance_summary_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/parse/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Parse Resume
         * @description Parse a resume file (PDF or DOCX) and extract structured data
         *
         *     Args:
         *         file: Uploaded resume file
         *         use_case: Parse resume use case (injected)
         *
         *     Returns:
         *         Parsed resume data
         *
         *     Raises:
         *         HTTPException: If parsing fails
         */
        post: operations["parse_resume_api_v1_parse_resume_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/jd/analyze": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Analyze Job Description
         * @description Analyze job description and extract structured information
         *
         *     This endpoint:
         *     1. Extracts company, position, and industry
         *     2. Identifies required and preferred skills
         *     3. Extracts responsibilities and qualifications
         *     4. Generates weighted keywords for matching
         *
         *     Args:
         *         request: Job description text
         *
         *     Returns:
         *         Analyzed job description with extracted information
         *
         *     Example:
         *         ```json
         *         {
         *             "raw_text": "Senior Backend Engineer at Acme Corp..."
         *         }
         *         ```
         */
        post: operations["analyze_job_description_api_v1_jd_analyze_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/master/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Master Resume
         * @description Get the user's master resume
         *
         *     Returns:
         *         Master resume if exists, 404 otherwise
         */
        get: operations["get_master_resume_api_v1_master_resume_get"];
        /**
         * Update Master Resume
         * @description Update master resume
         *
         *     Args:
         *         request: Updated master resume data
         *
         *     Returns:
         *         Updated master resume
         */
        put: operations["update_master_resume_api_v1_master_resume_put"];
        /**
         * Create Master Resume
         * @description Create a new master resume
         *
         *     This creates the master resume that contains all your experiences,
         *     projects, and skills. You'll use this to generate tailored resumes.
         *
         *     Args:
         *         request: Master resume data
         *
         *     Returns:
         *         Created master resume
         */
        post: operations["create_master_resume_api_v1_master_resume_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tailor/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Tailor Resume
         * @description Create a tailored resume from master resume based on JD
         *
         *     This endpoint:
         *     1. Selects most relevant experiences from master resume
         *     2. Selects best bullet points for each experience
         *     3. Optimizes bullets using STAR framework and JD keywords
         *     4. Calculates match score and ATS score
         *
         *     Args:
         *         request: Master resume ID and JD ID
         *
         *     Returns:
         *         Tailored resume with optimized content
         *
         *     Example:
         *         ```json
         *         {
         *             "master_resume_id": "master-123",
         *             "jd_id": "jd-456"
         *         }
         *         ```
         */
        post: operations["tailor_resume_api_v1_tailor_resume_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tailor/resume/{tailored_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Tailored Resume
         * @description Get a tailored resume by ID
         *
         *     Args:
         *         tailored_id: Tailored resume ID
         *
         *     Returns:
         *         Tailored resume
         */
        get: operations["get_tailored_resume_api_v1_tailor_resume__tailored_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Runs */
        get: operations["list_runs_api_v1_agent_runs_get"];
        put?: never;
        /** Create Run */
        post: operations["create_run_api_v1_agent_runs_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Run */
        get: operations["get_run_api_v1_agent_runs__run_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Submit Resume */
        post: operations["submit_resume_api_v1_agent_runs__run_id__resume_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/job-description": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Submit Jd */
        post: operations["submit_jd_api_v1_agent_runs__run_id__job_description_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/messages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Send Message */
        post: operations["send_message_api_v1_agent_runs__run_id__messages_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/evidence": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Record Evidence */
        post: operations["record_evidence_api_v1_agent_runs__run_id__evidence_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/proposals/{proposal_id}/decisions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Decide */
        post: operations["decide_api_v1_agent_runs__run_id__proposals__proposal_id__decisions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/versions/{version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Version */
        get: operations["get_version_api_v1_agent_runs__run_id__versions__version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/versions/{version_id}/restore": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Restore */
        post: operations["restore_api_v1_agent_runs__run_id__versions__version_id__restore_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/versions/{version_id}/exports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Export */
        post: operations["create_export_api_v1_agent_runs__run_id__versions__version_id__exports_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/exports/{export_id}/download": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Download */
        get: operations["download_api_v1_agent_runs__run_id__exports__export_id__download_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/agent/runs/{run_id}/events": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Events */
        get: operations["events_api_v1_agent_runs__run_id__events_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health Check */
        get: operations["health_check_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /**
         * AnalyzeJDRequest
         * @description Request to analyze job description
         * @example {
         *       "raw_text": "\n                Senior Backend Engineer - Acme Corp\n\n                We are seeking a talented Senior Backend Engineer to join our team.\n\n                Requirements:\n                - 5+ years of experience in backend development\n                - Strong proficiency in Python and Go\n                - Experience with microservices architecture\n                - Expertise in PostgreSQL and Redis\n                - Kubernetes and Docker experience\n                - Strong problem-solving skills\n\n                Responsibilities:\n                - Design and implement scalable backend systems\n                - Lead technical discussions and architecture decisions\n                - Mentor junior engineers\n                - Collaborate with cross-functional teams\n                "
         *     }
         */
        AnalyzeJDRequest: {
            /**
             * Raw Text
             * @description Job description text (minimum 50 characters)
             */
            raw_text: string;
        };
        /**
         * AnalyzeJDResponse
         * @description Response from JD analysis
         */
        AnalyzeJDResponse: {
            /** Success */
            success: boolean;
            job_description?: components["schemas"]["JobDescriptionSchema"] | null;
            /** Error */
            error?: string | null;
        };
        /** Body_parse_resume_api_v1_parse_resume_post */
        Body_parse_resume_api_v1_parse_resume_post: {
            /** File */
            file: string;
        };
        /** Body_submit_resume_api_v1_agent_runs__run_id__resume_post */
        Body_submit_resume_api_v1_agent_runs__run_id__resume_post: {
            /** File */
            file: string;
        };
        /**
         * BuildResumeRequest
         * @description Complete resume data from frontend form
         */
        BuildResumeRequest: {
            contact: components["schemas"]["agent_service__api__routes__build__ContactInfo"];
            /** Experience */
            experience: components["schemas"]["agent_service__api__routes__build__ExperienceInfo"][];
            /** Education */
            education: components["schemas"]["agent_service__api__routes__build__EducationInfo"][];
            /** Skills */
            skills: string[];
            /** Summary */
            summary?: string | null;
            /** Targetjob */
            targetJob?: string | null;
            /**
             * Enhancewithai
             * @default false
             */
            enhanceWithAI: boolean;
        };
        /**
         * BulletOptimizationSchema
         * @description Schema for bullet point optimization
         * @example {
         *       "bullet_id": "bullet-123",
         *       "improvements": [
         *         "Added quantifiable metrics (300%, 2s→0.5s)",
         *         "Stronger action verb (Spearheaded vs Led)",
         *         "Added team size context (5 engineers)"
         *       ],
         *       "keyword_matches": [
         *         "optimize",
         *         "performance",
         *         "latency"
         *       ],
         *       "optimized_text": "Spearheaded team of 5 engineers to optimize system performance by 300%, reducing latency from 2s to 0.5s",
         *       "original_text": "Led team to improve system performance",
         *       "status": "pending"
         *     }
         */
        BulletOptimizationSchema: {
            /** Bullet Id */
            bullet_id: string;
            /** Original Text */
            original_text: string;
            /** Optimized Text */
            optimized_text: string;
            /**
             * Improvements
             * @default []
             */
            improvements: string[];
            /**
             * Keyword Matches
             * @default []
             */
            keyword_matches: string[];
            /**
             * Status
             * @description pending, accepted, rejected
             * @default pending
             */
            status: string;
        };
        /**
         * BulletPointSchema
         * @description Schema for bullet point
         */
        BulletPointSchema: {
            /** Id */
            id?: string | null;
            /** Text */
            text: string;
            /** Keywords */
            keywords?: string[];
            /** Skills Used */
            skills_used?: string[];
        };
        /** CreateExportRequest */
        CreateExportRequest: {
            /**
             * Format
             * @enum {string}
             */
            format: "pdf" | "docx";
            /** Idempotency Key */
            idempotency_key: string;
        };
        /**
         * CreateMasterResumeRequest
         * @description Request to create master resume from parsed resume
         */
        CreateMasterResumeRequest: {
            personal_info?: components["schemas"]["PersonalInfoSchema-Input"] | null;
            /** Experiences */
            experiences?: components["schemas"]["ExperienceSchema-Input"][];
            /** Education */
            education?: components["schemas"]["EducationSchema-Input"][];
            /** Skills */
            skills?: components["schemas"]["SkillSchema-Input"][];
        };
        /** DecisionRecord */
        DecisionRecord: {
            /** Id */
            id: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Proposal Id */
            proposal_id: string;
            /** Proposal Revision */
            proposal_revision: number;
            /** Decision */
            decision: string;
            /** Version Id */
            version_id: string | null;
        };
        /**
         * EducationSchema
         * @description Schema for education
         */
        "EducationSchema-Input": {
            /** Id */
            id?: string | null;
            /** School */
            school?: string | null;
            /** Degree */
            degree?: string | null;
            /** Start Date */
            start_date?: string | null;
            /** End Date */
            end_date?: string | null;
            /** Description */
            description?: string | null;
        };
        /** EnhanceRequest */
        EnhanceRequest: {
            /** Description */
            description: string;
            /** Jobtitle */
            jobTitle?: string | null;
            /** Company */
            company?: string | null;
        };
        /** EnhanceResponse */
        EnhanceResponse: {
            /** Success */
            success: boolean;
            /** Enhanced */
            enhanced: string;
        };
        /** EnhanceSummaryRequest */
        EnhanceSummaryRequest: {
            /** Summary */
            summary: string;
            /** Targetjob */
            targetJob?: string | null;
            /** Skills */
            skills?: string[] | null;
            /** Yearsofexperience */
            yearsOfExperience?: number | null;
        };
        /** EvidenceRequest */
        EvidenceRequest: {
            /** Content */
            content: string;
        };
        /**
         * ExperienceSchema
         * @description Schema for experience with bullets
         */
        "ExperienceSchema-Input": {
            /** Id */
            id?: string | null;
            /** Company */
            company?: string | null;
            /** Title */
            title?: string | null;
            /** Location */
            location?: string | null;
            /** Start Date */
            start_date?: string | null;
            /** End Date */
            end_date?: string | null;
            /** Description */
            description?: string | null;
            /** Bullets */
            bullets?: components["schemas"]["BulletPointSchema"][];
            /** Skills Used */
            skills_used?: string[];
            /** Industry */
            industry?: string | null;
        };
        /** ExportRecord */
        ExportRecord: {
            /** Id */
            id: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Version Id */
            version_id: string;
            /** Content Type */
            content_type: string;
            /** Size Bytes */
            size_bytes: number;
        };
        /**
         * GenerateResumeRequest
         * @description Request to generate resume file
         */
        GenerateResumeRequest: {
            resumeData: components["schemas"]["ResumeData"];
            /** Template */
            template: string;
            /**
             * Format
             * @enum {string}
             */
            format: "pdf" | "word";
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** JobDescriptionRequest */
        JobDescriptionRequest: {
            /** Content */
            content: string;
        };
        /**
         * JobDescriptionSchema
         * @description Schema for analyzed job description
         * @example {
         *       "company": "Acme Corp",
         *       "keywords": [
         *         {
         *           "category": "required",
         *           "text": "microservices",
         *           "weight": 0.9
         *         },
         *         {
         *           "category": "required",
         *           "text": "scalability",
         *           "weight": 0.8
         *         }
         *       ],
         *       "position": "Senior Backend Engineer",
         *       "preferred_skills": [
         *         "Go",
         *         "Redis",
         *         "AWS"
         *       ],
         *       "raw_text": "We are looking for a Senior Backend Engineer...",
         *       "required_skills": [
         *         "Python",
         *         "PostgreSQL",
         *         "Kubernetes"
         *       ]
         *     }
         */
        JobDescriptionSchema: {
            /** Id */
            id?: string | null;
            /** Raw Text */
            raw_text: string;
            /** Company */
            company?: string | null;
            /** Position */
            position?: string | null;
            /**
             * Required Skills
             * @default []
             */
            required_skills: string[];
            /**
             * Preferred Skills
             * @default []
             */
            preferred_skills: string[];
            /**
             * Responsibilities
             * @default []
             */
            responsibilities: string[];
            /**
             * Qualifications
             * @default []
             */
            qualifications: string[];
            /** Industry */
            industry?: string | null;
            /**
             * Keywords
             * @default []
             */
            keywords: components["schemas"]["KeywordWeightSchema"][];
            /** Analyzed At */
            analyzed_at?: string | null;
        };
        /** JobDescriptionSource */
        JobDescriptionSource: {
            /** Id */
            id: string;
            /** Raw Text */
            raw_text: string;
            /** Analysis */
            analysis: {
                [key: string]: unknown;
            };
        };
        /**
         * KeywordWeightSchema
         * @description Schema for weighted keyword
         */
        KeywordWeightSchema: {
            /** Text */
            text: string;
            /**
             * Weight
             * @description Weight from 0 to 1
             */
            weight: number;
            /**
             * Category
             * @description Category: required, preferred, nice_to_have
             */
            category: string;
        };
        /**
         * MasterResumeSchema
         * @description Schema for master resume
         * @example {
         *       "experiences": [
         *         {
         *           "bullets": [
         *             {
         *               "keywords": [
         *                 "microservices",
         *                 "architecture",
         *                 "leadership"
         *               ],
         *               "skills_used": [
         *                 "Kubernetes",
         *                 "Docker",
         *                 "Python"
         *               ],
         *               "text": "Led migration of monolithic architecture to microservices"
         *             }
         *           ],
         *           "company": "Google",
         *           "end_date": "2023-12",
         *           "industry": "Tech",
         *           "skills_used": [
         *             "Python",
         *             "Kubernetes",
         *             "Docker"
         *           ],
         *           "start_date": "2021-01",
         *           "title": "Senior Software Engineer"
         *         }
         *       ],
         *       "personal_info": {
         *         "email": "john@example.com",
         *         "name": "John Doe"
         *       }
         *     }
         */
        MasterResumeSchema: {
            /** Id */
            id?: string | null;
            /** User Id */
            user_id?: string | null;
            personal_info?: components["schemas"]["agent_service__api__schemas__master_resume__PersonalInfoSchema"] | null;
            /** Experiences */
            experiences?: components["schemas"]["agent_service__api__schemas__master_resume__ExperienceSchema"][];
            /** Education */
            education?: components["schemas"]["agent_service__api__schemas__master_resume__EducationSchema"][];
            /** Skills */
            skills?: components["schemas"]["agent_service__api__schemas__master_resume__SkillSchema"][];
            /** Created At */
            created_at?: string | null;
            /** Updated At */
            updated_at?: string | null;
        };
        /** MessageRecord */
        MessageRecord: {
            /** Id */
            id: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Sequence */
            sequence: number;
            /** Role */
            role: string;
            /** Content */
            content: string;
        };
        /** MessageRequest */
        MessageRequest: {
            /** Content */
            content: string;
        };
        /** ParsedResumeSchema */
        ParsedResumeSchema: {
            personal_info?: components["schemas"]["agent_service__api__schemas__resume__PersonalInfoSchema"] | null;
            /** Experience */
            experience?: components["schemas"]["agent_service__api__schemas__resume__ExperienceSchema"][];
            /** Education */
            education?: components["schemas"]["agent_service__api__schemas__resume__EducationSchema"][];
            /** Skills */
            skills?: components["schemas"]["agent_service__api__schemas__resume__SkillSchema"][];
            /** Raw Text */
            raw_text?: string | null;
        };
        /**
         * PersonalInfoSchema
         * @description Schema for personal information
         */
        "PersonalInfoSchema-Input": {
            /** Name */
            name?: string | null;
            /** Email */
            email?: string | null;
            /** Phone */
            phone?: string | null;
            /** Linkedin */
            linkedin?: string | null;
            /** Github */
            github?: string | null;
        };
        /** ProposalDecisionRequest */
        ProposalDecisionRequest: {
            /**
             * Decision
             * @enum {string}
             */
            decision: "accepted" | "rejected" | "revision_requested";
            /** Expected Revision */
            expected_revision: number;
            /** Idempotency Key */
            idempotency_key: string;
            /** Version Name */
            version_name?: string | null;
        };
        /** ProposalRecord */
        ProposalRecord: {
            /** Id */
            id: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Revision */
            revision: number;
            /** Status */
            status: string;
            /** Affected Content */
            affected_content: string;
            /** Suggested Replacement */
            suggested_replacement: string;
            /** Jd Reason */
            jd_reason: string;
            /** Source Evidence */
            source_evidence: {
                [key: string]: unknown;
            };
            /** Evidence Request */
            evidence_request?: string | null;
        };
        /** RestoreVersionRequest */
        RestoreVersionRequest: {
            /** Idempotency Key */
            idempotency_key: string;
        };
        /**
         * ResumeData
         * @description Complete resume data
         */
        ResumeData: {
            contact: components["schemas"]["agent_service__api__routes__export__ContactInfo"];
            /** Experience */
            experience: components["schemas"]["agent_service__api__routes__export__ExperienceInfo"][];
            /** Education */
            education: components["schemas"]["agent_service__api__routes__export__EducationInfo"][];
            /** Skills */
            skills: string[];
            /**
             * Summary
             * @default
             */
            summary: string;
        };
        /** ResumeSource */
        ResumeSource: {
            /** Id */
            id: string;
            /** Filename */
            filename: string;
            /** Parsed Data */
            parsed_data: {
                [key: string]: unknown;
            };
        };
        /** RunListResponse */
        RunListResponse: {
            /** Items */
            items: components["schemas"]["RunSummary"][];
            /** Next Cursor */
            next_cursor?: string | null;
        };
        /** RunSnapshotResponse */
        RunSnapshotResponse: {
            run: components["schemas"]["RunSummary"];
            resume: components["schemas"]["ResumeSource"] | null;
            job_description: components["schemas"]["JobDescriptionSource"] | null;
            /** Messages */
            messages: components["schemas"]["MessageRecord"][];
            /** Proposals */
            proposals: components["schemas"]["ProposalRecord"][];
            /** Decisions */
            decisions: components["schemas"]["DecisionRecord"][];
            /** Versions */
            versions: components["schemas"]["VersionRecord"][];
            /** Exports */
            exports: components["schemas"]["ExportRecord"][];
            /** Latest Event Sequence */
            latest_event_sequence: number;
        };
        /** RunSummary */
        RunSummary: {
            /** Id */
            id: string;
            /** State */
            state: string;
            /** Revision */
            revision: number;
            /** Provider */
            provider: string;
            /** Model */
            model: string;
            /** Current Version Id */
            current_version_id: string | null;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
        };
        /**
         * SkillSchema
         * @description Schema for skill
         */
        "SkillSchema-Input": {
            /** Name */
            name: string;
            /** Category */
            category?: string | null;
        };
        /**
         * TailorResumeRequest
         * @description Request to create tailored resume
         * @example {
         *       "jd_id": "jd-456",
         *       "master_resume_id": "master-resume-123"
         *     }
         */
        TailorResumeRequest: {
            /** Master Resume Id */
            master_resume_id: string;
            /** Jd Id */
            jd_id: string;
        };
        /**
         * TailorResumeResponse
         * @description Response from tailoring resume
         */
        TailorResumeResponse: {
            /** Success */
            success: boolean;
            tailored_resume?: components["schemas"]["TailoredResumeSchema"] | null;
            /** Error */
            error?: string | null;
        };
        /**
         * TailoredResumeSchema
         * @description Schema for tailored resume
         */
        TailoredResumeSchema: {
            /** Id */
            id?: string | null;
            /** Master Resume Id */
            master_resume_id: string;
            /** Jd Id */
            jd_id: string;
            /**
             * Selected Experience Ids
             * @default []
             */
            selected_experience_ids: string[];
            /**
             * Selected Bullet Optimizations
             * @default []
             */
            selected_bullet_optimizations: components["schemas"]["BulletOptimizationSchema"][];
            /**
             * Selected Education Ids
             * @default []
             */
            selected_education_ids: string[];
            /**
             * Selected Skills
             * @default []
             */
            selected_skills: string[];
            /** Match Score */
            match_score: number;
            /** Ats Score */
            ats_score: number;
            /** Created At */
            created_at?: string | null;
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
            /** Input */
            input?: unknown;
            /** Context */
            ctx?: Record<string, never>;
        };
        /** VersionRecord */
        VersionRecord: {
            /** Id */
            id: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Version Number */
            version_number: number;
            /** Version Name */
            version_name: string;
            /** Parent Version Id */
            parent_version_id: string | null;
            /** Content */
            content: {
                [key: string]: unknown;
            };
        };
        /**
         * ContactInfo
         * @description Contact information from frontend
         */
        agent_service__api__routes__build__ContactInfo: {
            /** Fullname */
            fullName: string;
            /** Email */
            email: string;
            /** Phone */
            phone: string;
            /** Location */
            location?: string | null;
            /** Title */
            title?: string | null;
        };
        /**
         * EducationInfo
         * @description Education entry from frontend
         */
        agent_service__api__routes__build__EducationInfo: {
            /** Degree */
            degree: string;
            /** School */
            school: string;
            /** Startdate */
            startDate: string;
            /** Enddate */
            endDate?: string | null;
            /** Location */
            location?: string | null;
        };
        /**
         * ExperienceInfo
         * @description Experience entry from frontend
         */
        agent_service__api__routes__build__ExperienceInfo: {
            /** Position */
            position: string;
            /** Company */
            company: string;
            /** Startdate */
            startDate: string;
            /** Enddate */
            endDate?: string | null;
            /** Location */
            location?: string | null;
            /** Description */
            description?: string | null;
        };
        /**
         * ContactInfo
         * @description Contact information from frontend
         */
        agent_service__api__routes__export__ContactInfo: {
            /** Fullname */
            fullName: string;
            /** Email */
            email: string;
            /** Phone */
            phone: string;
            /**
             * Location
             * @default
             */
            location: string;
            /**
             * Title
             * @default
             */
            title: string;
        };
        /**
         * EducationInfo
         * @description Education entry from frontend
         */
        agent_service__api__routes__export__EducationInfo: {
            /** Degree */
            degree: string;
            /** School */
            school: string;
            /** Startdate */
            startDate: string;
            /**
             * Enddate
             * @default
             */
            endDate: string;
            /**
             * Location
             * @default
             */
            location: string;
        };
        /**
         * ExperienceInfo
         * @description Experience entry from frontend
         */
        agent_service__api__routes__export__ExperienceInfo: {
            /** Position */
            position: string;
            /** Company */
            company: string;
            /** Startdate */
            startDate: string;
            /**
             * Enddate
             * @default
             */
            endDate: string;
            /**
             * Location
             * @default
             */
            location: string;
            /**
             * Description
             * @default
             */
            description: string;
        };
        /**
         * EducationSchema
         * @description Schema for education
         */
        agent_service__api__schemas__master_resume__EducationSchema: {
            /** Id */
            id?: string | null;
            /** School */
            school?: string | null;
            /** Degree */
            degree?: string | null;
            /** Start Date */
            start_date?: string | null;
            /** End Date */
            end_date?: string | null;
            /** Description */
            description?: string | null;
        };
        /**
         * ExperienceSchema
         * @description Schema for experience with bullets
         */
        agent_service__api__schemas__master_resume__ExperienceSchema: {
            /** Id */
            id?: string | null;
            /** Company */
            company?: string | null;
            /** Title */
            title?: string | null;
            /** Location */
            location?: string | null;
            /** Start Date */
            start_date?: string | null;
            /** End Date */
            end_date?: string | null;
            /** Description */
            description?: string | null;
            /** Bullets */
            bullets?: components["schemas"]["BulletPointSchema"][];
            /** Skills Used */
            skills_used?: string[];
            /** Industry */
            industry?: string | null;
        };
        /**
         * PersonalInfoSchema
         * @description Schema for personal information
         */
        agent_service__api__schemas__master_resume__PersonalInfoSchema: {
            /** Name */
            name?: string | null;
            /** Email */
            email?: string | null;
            /** Phone */
            phone?: string | null;
            /** Linkedin */
            linkedin?: string | null;
            /** Github */
            github?: string | null;
        };
        /**
         * SkillSchema
         * @description Schema for skill
         */
        agent_service__api__schemas__master_resume__SkillSchema: {
            /** Name */
            name: string;
            /** Category */
            category?: string | null;
        };
        /** EducationSchema */
        agent_service__api__schemas__resume__EducationSchema: {
            /** School */
            school?: string | null;
            /** Degree */
            degree?: string | null;
            /** Start Date */
            start_date?: string | null;
            /** End Date */
            end_date?: string | null;
            /** Description */
            description?: string | null;
        };
        /** ExperienceSchema */
        agent_service__api__schemas__resume__ExperienceSchema: {
            /** Company */
            company?: string | null;
            /** Title */
            title?: string | null;
            /** Location */
            location?: string | null;
            /** Start Date */
            start_date?: string | null;
            /** End Date */
            end_date?: string | null;
            /** Description */
            description?: string | null;
        };
        /** PersonalInfoSchema */
        agent_service__api__schemas__resume__PersonalInfoSchema: {
            /** Name */
            name?: string | null;
            /** Email */
            email?: string | null;
            /** Phone */
            phone?: string | null;
            /** Linkedin */
            linkedin?: string | null;
            /** Github */
            github?: string | null;
        };
        /** SkillSchema */
        agent_service__api__schemas__resume__SkillSchema: {
            /** Name */
            name: string;
            /** Category */
            category?: string | null;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    build_resume_api_v1_resume_build__post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BuildResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    validate_resume_data_api_v1_resume_build_validate_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BuildResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    generate_preview_api_v1_resume_build_preview_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BuildResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    generate_resume_api_v1_resume_generate_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenerateResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    enhance_content_api_v1_resume_enhance_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EnhanceRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EnhanceResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    enhance_summary_api_v1_resume_enhance_summary_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EnhanceSummaryRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EnhanceResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    parse_resume_api_v1_parse_resume_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_parse_resume_api_v1_parse_resume_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ParsedResumeSchema"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    analyze_job_description_api_v1_jd_analyze_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AnalyzeJDRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AnalyzeJDResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_master_resume_api_v1_master_resume_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MasterResumeSchema"];
                };
            };
        };
    };
    update_master_resume_api_v1_master_resume_put: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CreateMasterResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MasterResumeSchema"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_master_resume_api_v1_master_resume_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CreateMasterResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    tailor_resume_api_v1_tailor_resume_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TailorResumeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TailorResumeResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_tailored_resume_api_v1_tailor_resume__tailored_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                tailored_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TailoredResumeSchema"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_runs_api_v1_agent_runs_get: {
        parameters: {
            query?: {
                limit?: number;
                before?: string | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunListResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_run_api_v1_agent_runs_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
        };
    };
    get_run_api_v1_agent_runs__run_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    submit_resume_api_v1_agent_runs__run_id__resume_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_submit_resume_api_v1_agent_runs__run_id__resume_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    submit_jd_api_v1_agent_runs__run_id__job_description_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["JobDescriptionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    send_message_api_v1_agent_runs__run_id__messages_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MessageRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    record_evidence_api_v1_agent_runs__run_id__evidence_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EvidenceRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    decide_api_v1_agent_runs__run_id__proposals__proposal_id__decisions_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                proposal_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProposalDecisionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_version_api_v1_agent_runs__run_id__versions__version_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VersionRecord"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    restore_api_v1_agent_runs__run_id__versions__version_id__restore_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                version_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RestoreVersionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RunSnapshotResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_export_api_v1_agent_runs__run_id__versions__version_id__exports_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                version_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CreateExportRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExportRecord"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    download_api_v1_agent_runs__run_id__exports__export_id__download_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                export_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    events_api_v1_agent_runs__run_id__events_get: {
        parameters: {
            query?: {
                after?: number;
            };
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    health_check_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
        };
    };
}
