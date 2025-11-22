"""
Predefined course category codes (like EE, CS, HU, etc.)
These are standard university course prefixes.
"""

COURSE_CATEGORY_CODES = [
    ('', 'Select a category (optional)'),
    ('AA', 'AA - African American Studies'),
    ('ACC', 'ACC - Accounting'),
    ('AE', 'AE - Aerospace Engineering'),
    ('ARCH', 'ARCH - Architecture'),
    ('ART', 'ART - Art'),
    ('BIO', 'BIO - Biology'),
    ('BUS', 'BUS - Business'),
    ('CE', 'CE - Civil Engineering'),
    ('CHEM', 'CHEM - Chemistry'),
    ('CS', 'CS - Computer Science'),
    ('ECON', 'ECON - Economics'),
    ('EE', 'EE - Electrical Engineering'),
    ('ENG', 'ENG - English'),
    ('ENV', 'ENV - Environmental Science'),
    ('FIN', 'FIN - Finance'),
    ('HIST', 'HIST - History'),
    ('HU', 'HU - Humanities'),
    ('IE', 'IE - Industrial Engineering'),
    ('LAW', 'LAW - Law'),
    ('MATH', 'MATH - Mathematics'),
    ('ME', 'ME - Mechanical Engineering'),
    ('MED', 'MED - Medicine'),
    ('MUS', 'MUS - Music'),
    ('PHIL', 'PHIL - Philosophy'),
    ('PHY', 'PHY - Physics'),
    ('PSY', 'PSY - Psychology'),
    ('PE', 'PE - Physical Education'),
    ('SOC', 'SOC - Sociology'),
    ('STAT', 'STAT - Statistics'),
    ('OTHER', 'Other (specify)')
]

def get_category_code_choices():
    """Get list of category code choices for dropdown"""
    return COURSE_CATEGORY_CODES

def normalize_category_code(code):
    """Normalize category code to uppercase and strip whitespace"""
    if code:
        return code.upper().strip()
    return None

