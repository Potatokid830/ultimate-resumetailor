# Fictional "Mingyuan (Alex) Li" – English resume for a strategy / business analyst internship.
# Run (from any working folder): bash <skill>/scripts/build.sh <skill>/examples/example_en.py Mingyuan_Li_Resume_Strategy en
# Every school, company and number here is made up; it only shows the writing pattern:
# analysis -> judgement -> recommendation -> result.
from helpers_en import *

body = header(info_line='Available full-time from Dec 2026 for 6 months (4 days a week)') + [
    section('Education'),
    entry('Example University', 'Shanghai, China'),
    sub('Bachelor of Economics, Quantitative Economics', 'Sep 2023 – Jun 2027'),
    bullet('**Relevant coursework:** Econometrics, Statistics, Microeconomics, Databases, Marketing, Corporate Finance'),
    bullet('**Honours:** University Scholarship (top 15%); provincial 2nd prize, National Market Research Competition'),

    section('Experience'),
    entry('Example Securities – Research Institute, Internet & Media Team', 'Shanghai, China'),
    sub('Equity Research Intern', 'Jul 2025 – Dec 2025'),
    bullet('Broke down ad monetisation at three leading short-video platforms (daily users × ad load × price), concluded that feed-ad growth would slow while local-services commission becomes the next driver, and wrote the core chapters of a 12,000-word sector report – **the view was adopted in the team’s investor roadshow deck**.'),
    bullet('Built a quarterly tracker of monthly users and ad revenue for 8 companies over 20 quarters in Excel; spotted one platform’s ad revenue growing slower than its users for two straight quarters, flagging weaker monetisation and supporting a cut to the team’s earnings forecast.'),
    bullet('Organised 120+ filings and earnings-call notes into a knowledge base tagged by users, monetisation and cost, cutting new analysts’ research time from half a day to about an hour.'),
    entry('Example Consumer Goods Co. – E-commerce Growth', 'Hangzhou, China'),
    sub('Data Analyst Intern', 'Jan 2025 – Mar 2025'),
    bullet('Pulled 12 months of order and membership data with SQL and decomposed a GMV decline into traffic, conversion, basket size and repeat purchase; found a ~6-point fall in repeat rate among existing customers, not traffic, was the main cause.'),
    bullet('Proposed tiered membership with repeat-purchase coupons and helped design the A/B test; after a 4-week pilot the test group’s repeat rate was 3.1 points higher than control, and **the plan was rolled out to all Tmall stores**.'),
    bullet('Rebuilt the weekly store dashboard in Power BI, cutting 30+ metrics down to 8 core ones and roughly halving the weekly review meeting.'),

    section('Projects'),
    entry('Instant Retail – Consumer Survey & Market Entry', 'Course project, 4-person team, Oct 2024'),
    bullet('Designed the survey and ran the analysis on 412 valid responses (cross-tabs, simple regression); delivery speed had the strongest link to repeat intent (r = 0.58), so the team recommended starting 30-minute delivery in dense neighbourhoods; graded A.'),
    entry('Campus Second-hand Book Mini-program', 'Personal project, Mar 2024 – Aug 2024'),
    bullet('Took it from user pain point and competitor review to launch: 1,600 sign-ups and about 2,300 orders; after reviewing acquisition cost and strong graduation-season cyclicality, judged it could not stay profitable and wound it down, writing up the lessons.'),

    section('Leadership & Activities'),
    entry('Student Union, School of Economics – External Relations', 'Head of Department, Sep 2024 – Jun 2025'),
    bullet('Partnered with 12 employers on campus recruiting talks, ran 3 industry sessions with about 600 attendees, and turned sponsorship outreach into a standard playbook and pricing sheet – sponsorship income rose about 40% year on year.'),

    section('Skills & Certifications'),
    bullet('**Analysis:** industry research, GMV decomposition, customer segmentation, A/B test design, survey design and interviews, regression'),
    bullet('**Tools:** Excel (pivot tables, lookups), SQL (joins, aggregation, window functions), Power BI, Python (pandas, working knowledge), PowerPoint'),
    bullet('**Languages & certifications:** Mandarin (native), English (professional working proficiency, CET-6 610); Securities Qualification Certificate (2024)'),
]
finish(body)
