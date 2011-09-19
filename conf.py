"""
Some constant values used throughout the application
"""




# The date of the monday in the first week of the gehol calendar. This will be changed once a year.
FIRST_MONDAY = "19/09/2011"

# the weekspans of the various periods in the academic year
ALL_YEAR_WEEKSPAN = "1-36"
Q1_WEEKSPAN = "1-14"
Q2_WEEKSPAN = "21-36"
JANUARY_EXAMS_WEEKSPAN = "17-19"
JUNE_EXAMS_WEEKSPAN = "38-40"
SEPTEMBER_EXAMS_WEEKSPAN = "48-51"


# There are 3 exam sessions. It's not useful to list them all year long.

CURRENT_EXAM_SESSION = None
EXAM_SESSION_WEEKSPANS = {'january':JANUARY_EXAMS_WEEKSPAN,
                          'june':JUNE_EXAMS_WEEKSPAN,
                        'september':SEPTEMBER_EXAMS_WEEKSPAN}


# A bunch of URLs and URL templates
GEHOL_FRONTEND_URL = 'scientia-web.ulb.ac.be'
SCIENTIA_BACKEND_HOST = "164.15.72.157:8081"
# params are steudentset id and weekspan
GEHOL_STUDENTSET_URL_TEMPLATE = "http://164.15.72.157:8081/Reporting/Individual;Student%%20Set%%20Groups;id;%s?&template=Ann%%E9e%%20d%%27%%E9tude&weeks=%s&days=1-6&periods=5-33&width=0&height=0"
# param is course mnemonic and weekspan
GEHOL_COURSE_URL_TEMPLATE = "http://164.15.72.157:8081/Reporting/Individual;Courses;name;%s?&days=1-6&height=0&width=0&periods=5-29&template=cours&weeks=%s"

# qrcode urls templates.
WEBCAL_BASE_URL = "webcal://geholimport.appspot.com%s"
BASE_URL = "http://geholimport.appspot.com"
COURSE_QRCODE_URL_TEMPLATE = "http://chart.apis.google.com/chart?cht=qr&chl="+BASE_URL+"/course/%s&chs=%dx%d"
STUDENTSET_QRCODE_URL_TEMPLATE = "http://chart.apis.google.com/chart?cht=qr&chl="+BASE_URL+"/student_set/m/%s&chs=%dx%d"



QRCODE_SAMPLE_URL = "https://twitter.com/oprah/status/1542224596"