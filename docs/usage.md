# Usage Guide - ai-email-assistant

## Getting Started

### Launching the Application
```bash
# Local installation
streamlit run src/ui/streamlit_app.py

# Using script
./scripts/run_local.sh

# Docker
docker-compose up

# Access at: http://localhost:8501
```

## Generating Your First Email

### Basic Workflow

1. **Select User Profile** (Sidebar)
2. **Choose Email Tone** (Sidebar)
3. **Enter Email Request** (Main area)
4. **Click "Generate Email"**
5. **Review and Export**

### Step-by-Step Example

#### Step 1: Select Your Profile

In the sidebar, choose the profile that matches your role:

- **Software Engineer**: Technical, professional communications
- **Student**: Academic, respectful communications
- **Teacher**: Educational, encouraging communications
- **Musician**: Creative, expressive communications
- **Business Executive**: Strategic, authoritative communications
- **Freelancer**: Friendly, collaborative communications

#### Step 2: Choose Tone

Use the tone slider to select:

- **Very Formal**: Ceremonial, highly respectful
- **Formal**: Professional, respectful
- **Professional**: Business-appropriate, polished (default)
- **Friendly**: Warm, personable
- **Casual**: Relaxed, informal

#### Step 3: Describe Your Email

Enter a clear description of what you want to write:

**Good Examples**:
```
"Write a follow-up email to my professor asking about
the research project deadline extension I requested last week."

"Thank my colleague Alex for helping me debug the authentication
issue yesterday."

"Request a meeting with my manager to discuss the Q3 project timeline."
```

**Poor Examples** (too vague):
```
"Email my professor"  # Missing purpose
"Send something"      # No context
"Write email"         # No details
```

#### Step 4: Generate Email

Click the **"Generate Email"** button. Typical generation time: 15-25 seconds.

#### Step 5: Review Generated Email

The email appears with: subject line, greeting, body content, closing, and your signature (from profile).

**Generation Details** (expandable): profile used, tone applied, detected intent, timestamp.

## Using Email Templates

Quick-start templates are available in the right column:

| Template | Use When |
|----------|----------|
| Follow-up | Checking on previous communication |
| Request | Asking for something specific |
| Thank You | Expressing gratitude |
| Apology | Acknowledging a mistake |
| Introduction | First contact with someone |

### Using Templates

1. Click a template button
2. Template text appears in input area
3. Complete the sentence with your specific details
4. Generate email

## Context-Aware Email Generation

### Enabling Context Memory

In the sidebar, check **"Use conversation history"**

When enabled:
- System remembers your last 3 emails
- Maintains conversational continuity
- References previous discussions

### How Context Works

**First Email**: Standard email based on prompt
**Second Email** (with context): References the previous request
**Third Email** (with context): Maintains full conversation thread

### When to Use Context

**Use context for**: Follow-up emails, ongoing conversations, related communications, series of emails to same person.

**Disable context for**: Completely new topics, different recipients, unrelated communications, starting fresh.

### Clearing History

Click **"Clear History"** in sidebar to reset conversation memory.

## Exporting Emails

### Export Options

#### 1. Copy to Clipboard
Click **"Copy to Clipboard"** - email appears in code block for selection.

#### 2. Download as TXT
Click **"Download TXT"** - includes metadata header and email content.

Filename format: `email_YYYYMMDD_HHMMSS.txt`

#### 3. Download as JSON
Click **"Download JSON"** - structured data with export metadata.

Filename format: `email_YYYYMMDD_HHMMSS.json`

### Use Cases for Each Format

| Format | Best For |
|--------|----------|
| TXT | Simple reference, printing, plain text editors |
| JSON | Integration with other tools, batch processing, data analysis, backup with metadata |

## Regenerating Emails

### When to Regenerate
- Tone doesn't match expectations
- Content needs adjustment
- Want alternative phrasing

### How to Regenerate
1. Review generated email
2. Click **"Regenerate"** button
3. New version generated with same prompt

### Improving Results

If regeneration doesn't help:
1. **Add more detail** to your prompt
2. **Change tone** setting
3. **Modify profile** if needed
4. **Adjust context** usage
5. **Clarify intent** in description

## Understanding Generation Details

### Intent Detection

The system identifies your email's purpose:

| Intent | Description |
|--------|-------------|
| Request | Asking for something |
| Response | Replying to inquiry |
| Follow-up | Continuing conversation |
| Notification | Informing about something |
| Apology | Expressing regret |
| Gratitude | Thanking someone |
| Introduction | Meeting new contact |
| Proposal | Suggesting something |
| Complaint | Expressing dissatisfaction |

## Best Practices

### Writing Effective Prompts

**Be Specific**: "Request project deadline extension due to illness" (not "Email about project")

**Provide Context**: "Follow up on my meeting request from last Tuesday about the Q3 budget review" (not "Follow up")

**Include Key Details**: "Thank my team lead Sarah for mentoring me on the API integration over the past month" (not "Thank someone")

**Mention Recipient When Relevant**: "Ask my professor Dr. Smith about office hours this week" (not "Ask about schedule")

### Choosing the Right Tone

| Tone | Best For |
|------|----------|
| Very Formal | Senior executives, ceremonial, legal correspondence |
| Formal | Initial contact with professors, client communications |
| Professional | Standard workplace, academic, most business interactions |
| Friendly | Known colleagues, team communications |
| Casual | Close collaborators, internal team chats |

### Profile Selection Tips

| Scenario | Profile | Tone |
|----------|---------|------|
| Request to professor | Student | Professional |
| Thank colleague | Software Engineer | Friendly |
| Parent-teacher email | Teacher | Professional |
| Band booking inquiry | Musician | Friendly |
| Investor update | Business Executive | Formal |
| Client proposal | Freelancer | Professional |

## Advanced Features

### Multi-Step Email Conversations

Use context memory for email series:

1. **Day 1**: Initial request → Standard email
2. **Day 3**: Follow-up (context enabled) → References initial request
3. **Day 5**: Confirmation (context enabled) → References the meeting
4. **Day 6**: Thank you (context enabled) → References meeting discussion

### Handling Complex Scenarios

**Sensitive Topics**: Provide full context, use formal tone, review carefully, consider regenerating for alternatives.

**Multi-Party Communications**: Mention all recipients in your prompt.

**Technical Communications**: Select appropriate profile, include specific technical terms, mention relevant technologies.

## Limitations and Considerations

### What the System Does Well
- Standard professional emails
- Academic communications
- Follow-up messages, thank you notes
- Meeting requests, status updates, introductions

### What Requires Manual Review
Always review before sending: highly sensitive topics, legal implications, financial commitments, personnel matters, critical deadlines.

### When NOT to Use
- Emergency communications
- Time-critical urgent matters
- When exact wording is legally required
- Highly personal/emotional topics
- When recipient expects your personal voice

## Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| Email too formal | Move tone slider to "Friendly" or "Casual", regenerate |
| Lacks specific details | Add more details to prompt, mention names/dates/numbers |
| Wrong intent detected | Rephrase prompt clearly, explicitly state purpose |
| Context not being used | Verify checkbox is checked, ensure previous emails exist |
| Email too long/short | Specify length in prompt: "Write a brief..." or "Write a detailed..." |

## Support

- Check [Troubleshooting](#troubleshooting-common-issues)
- Review [Best Practices](#best-practices)
- See [API Reference](api_reference.md)
- Report issues at [https://github.com/vinaytocode/ai-email-assistant/issues](https://github.com/vinaytocode/ai-email-assistant/issues)

---

**Author**: Vinay K <itzvinay@gmail.com>
**Repository**: https://github.com/vinaytocode/ai-email-assistant
**Quick Reference**: See [Installation Guide](installation.md)
**Technical Details**: See [Architecture](architecture.md)
