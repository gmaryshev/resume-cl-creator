# Resume & Cover Letter Creator

A template-driven system for generating tailored resumes and cover letters in LaTeX format for different job applications.

## Overview

This project helps you create customized resume and cover letter pairs for job applications. It uses a modular LaTeX-based approach with reference templates and personal information sources to generate professional, ATS-friendly documents tailored to specific job descriptions.

## Project Structure

```
resume_cl_creator/
├── README.md                          # This file
├── .gitignore                         # Git ignore rules (excludes personal info)
├── wf.txt                             # Workflow instructions for `go wf.txt`
├── writing_rules.txt                  # General writing rules
├── workflow/                          # Context bundling tools and source registry
│   ├── bundle_context.py
│   ├── source_registry.json
│   └── README.md
├── tests/                             # Bundler tests
│
├── Reference_Latex_template/          # LaTeX template files for styling
│   └── Latex_resume_template/         # Example resume template
│       ├── main.tex                   # Main document
│       ├── work-experience.tex        # Experience section
│       ├── highlighted-projects.tex   # Projects section
│       ├── current-work.tex           # Current studies/work section
│       ├── skills-summarized.tex      # Skills section
│       └── service.tex                # Service/leadership section
│
├── Reference_info/                    # Your personal information sources
│   └── (LinkedIn profile, work journal reflections, etc.)
│
├── Reference_resumes/                 # Reference resume files
│   └── (Existing resume content)
│
├── Job_descriptions/                  # Job descriptions to tailor for
│   └── jobdesc                        # Example job descriptions
│
└── Output/                            # Generated resumes and cover letters
    └── resume_cl_[Job_Title]_[Version]/
        ├── resume.pdf
        ├── cover_letter.pdf
        ├── tips_[Job_Title].pdf                   # Interview prep and job assessment
        └── resume_cl_[Job_Title]_latex_[Version]/
            ├── main.tex
            ├── resume.tex
            └── cover_letter.tex
```

## Dependencies

### Required Software

- **LaTeX Distribution**: 
  - Ubuntu/Debian: `sudo apt install texlive-latex-base texlive-fonts-recommended texlive-latex-extra`
  - macOS: `brew install basictex` or install [MacTeX](https://tug.org/mactex/)
  - Windows: [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

- **Text Editor/IDE** (recommended):
  - VS Code with LaTeX Workshop extension
  - Or any text editor (Sublime, Vim, etc.)

### Optional but Recommended

- **LaTeX Workshop Extension** (if using VS Code):
  - Search for "LaTeX Workshop" by James Yu in VS Code extensions marketplace
  - Provides live preview and compilation features

## Setup

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd resume_cl_creator
```

### 2. Install LaTeX
Choose the appropriate installation method for your OS (see Dependencies section).

### 3. Customize Reference Templates and Information
- Review and customize `Reference_Latex_template/` for your preferred styling
- Update `Reference_info/` with your personal contact information and career details
- Store reference resume content in `Reference_resumes/`

### 4. Verify Setup
Test LaTeX compilation:
```bash
cd Reference_Latex_template/Latex_resume_template
pdflatex main.tex
```

If successful, you'll see a `main.pdf` file generated.

## Workflow Summary

The normal entry point is `go wf.txt`.

### Quick Start

1. Put the complete job description in `Job_descriptions/jobdesc`.
2. Tell the Copilot agent: `go wf.txt`.
3. The workflow runs the context bundler:

   ```bash
   python3 workflow/bundle_context.py Job_descriptions/jobdesc
   ```

4. The agent reads the generated `context.md` and `manifest.json` from the
   printed `.workflow/bundles/` directory.
5. The agent uses Copilot to summarize long-source requests recorded in the
   manifest, preserving source paths and factual traceability.
6. The agent generates and compiles the resume, cover letter, and interview
   tips, then records the application only after required PDFs compile and the
   output structure is verified.

If bundling fails, the workflow must stop without generating documents or
writing application-tracking rows.

### Context Bundling

The checked-in [source registry](workflow/source_registry.json) controls which
files are approved generation context. Source folders remain separate; the
bundler compacts their contents into a per-run package:

- `context.md` contains the job description, approved source content, and
  generation constraints.
- `manifest.json` records source groups, trust levels, SHA-256 hashes,
  character counts, and Copilot summarization requests.

Bundles are written to `.workflow/bundles/`, which is ignored by Git. Existing
bundle directories are never overwritten. Run the bundler manually with:

```bash
python3 workflow/bundle_context.py Job_descriptions/jobdesc
```

See [workflow/README.md](workflow/README.md) for bundler options.

### Quick Start: Creating Your First Resume & Cover Letter

#### Step 1: Analyze the Template
- Review `Reference_Latex_template/Latex_resume_template/main.tex`
- Study the structure, formatting, and commands used
- **Do NOT copy personal information** (it's already been anonymized)

#### Step 2: Gather Your Content
- Review your reference resume in `Reference_resumes/`
- Access your personal information from `Reference_info/`

#### Step 3: Read the Job Description
- Locate the job description in `Job_descriptions/`
- Extract key requirements, skills, and responsibilities

#### Step 4: Create Output Folder
Create a new folder in `Output/` following the naming convention:
```
resume_cl_(JobTitle_at_Company)_(version_number)/
```

Example:
```
Output/resume_cl_Full_Stack_Developer_at_Acme_Corp_1/
```

#### Step 5: Create LaTeX Files
Create two main documents:
- **resume.tex**: Tailor content to job requirements, emphasize relevant skills
- **cover_letter.tex**: Write a compelling letter addressing the hiring manager

Structure your resume.tex file with sections matching the template:
- Header (name, contact info)
- Education
- Relevant Skills
- Current Work/Studies
- Highlighted Projects
- Work Experience
- Service/Leadership
M sk
#### Step 5A: Create Interview Tips File
Create a **tips_Job_Title_at_Company.pdf** file containing:
- Assessment of the job and how well my skills match the position, reevaluate and be honest
- Tips and strategies to prepare for the interview
- Key points to research about the company

Example: `tips_Software_Engineer_at_Plexxis.pdf`

#### Step 6: Compile to PDF
In your output folder:
```bash
pdflatex main.tex
pdflatex main.tex  # Run twice for proper formatting
```

Or use VS Code's LaTeX Workshop for one-click compilation.

#### Step 7: Organize Files
Final structure should be:
```
Output/resume_cl_Full_Stack_Developer_at_Acme_Corp_1/
├── resume.pdf
├── cover_letter.pdf
├── tips_Full_Stack_Developer_at_Acme_Corp.pdf
└── resume_cl_Full_Stack_Developer_at_Acme_Corp_latex_1/
    ├── main.tex
    ├── resume.tex
    ├── cover_letter.tex
    ├── main.aux
    └── (other LaTeX build artifacts)
```

## Key Principles

1. **ATS-Friendly**: Resumes should be compatible with Applicant Tracking Systems
   - Use simple formatting
   - Avoid images and complex layouts in resume (cover letter can be fancier)
   - Use standard fonts

2. **Truthfulness**: Only claim technologies and experiences you actually have
   - Don't exaggerate your role or skills
   - Reference actual projects from your portfolio

3. **Job-Specific Tailoring**: Customize content for each position
   - Use keywords from the job description
   - Highlight relevant experience and skills
   - Order experience by relevance

4. **Template Reuse**: Leverage the reference template structure
   - Maintains consistent, professional styling
   - Speeds up creation of new documents
   - Easy to update if you change your preferred design

## Common Commands

### Compile LaTeX to PDF
```bash
pdflatex main.tex
```

### Clean LaTeX build artifacts (keep only .pdf and .tex)
```bash
rm -f *.aux *.fdb_latexmk *.fls *.log *.out *.synctex.gz
```

### Preview updates (with LaTeX Workshop)
- Edit .tex file and save
- Preview updates automatically in VS Code

## Tips & Best Practices

- **Keep versions organized**: Number versions for easy tracking of iterations
- **Test compilation**: Always compile locally before submitting
- **Backup originals**: Keep reference templates untouched as a backup
- **Git tracking**: The `.gitignore` file prevents accidental commits of personal information
- **Template naming**: Use descriptive folder names that include job title and company
- **Two-pass compilation**: Run `pdflatex` twice to ensure proper formatting, cross-references, and hyperlinks

## Customization

### Modifying the Template
1. Open files in `Reference_Latex_template/`
2. Edit the structure, fonts, colors, or spacing
3. Test your changes
4. Create a new version in Output when satisfied

### Adding New Sections
- Add a new .tex file for each section (e.g., `certifications.tex`)
- Include it in main.tex: `\input{certifications.tex}`
- Define custom commands in main.tex if needed

## Troubleshooting

### LaTeX Won't Compile
- Check for syntax errors in your .tex files
- Verify all `\input{}` commands reference existing files
- Ensure package dependencies are installed

### Missing Package Errors
- Install additional LaTeX packages:
  ```bash
  sudo apt install texlive-fonts-recommended texlive-latex-extra
  ```

### PDF Not Generated
- Check console output for error messages
- Verify you're running pdflatex in the correct directory
- Some editors require explicit build commands

## Notes

- The generation workflow is agent-driven, with `wf.txt` as the entry point.
- Context bundling is automated; document generation and LaTeX compilation
  still depend on the agent following the workflow instructions.
- Reference information, generated output, job descriptions, and tracking CSVs
  are excluded from Git by default because they may contain personal data.
- The `.workflow/` directory contains temporary per-run bundles and is ignored.

## License

Use this project for personal job applications.

## Support

For issues with LaTeX compilation:
- [LaTeX Stack Exchange](https://tex.stackexchange.com/)
- [LaTeX Workshop Documentation](https://github.com/James-Yu/LaTeX-Workshop)
- [Overleaf Learning](https://www.overleaf.com/learn)
