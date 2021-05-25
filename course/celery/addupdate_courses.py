def add_courses(year, term):
    """
    runs through all courses for a given term
    year should be int of year
    term should be letter (A,B,C)
    """

    year_term = str(year) + str(term)
    year = year_term[:-1]
    term = year_term[-1]
    domain = config.get("opendata", "domain")
    id = config.get("opendata", "id")
    key = config.get("opendata", "key")
    print(domain, id, key)
    OData = OpenData(base_url=domain, id=id, key=key)
    OData_lookup = OpenData(base_url=domain, id=id, key=key)
    data = OData.get_courses_by_term(year_term)
    # print(data)
    page = 1

    while data != None:
        print("\n\tSTARTING PAGE : ", page, "\n")
        for datum in data[:10]:
            datum["section_id"] = datum["section_id"].replace(" ", "")
            datum["crosslist_primary"] = datum["section_id"].replace(" ", "")
            print("adding ", datum["section_id"])
            try:
                subject = Subject.objects.get(abbreviation=datum["course_department"])
            except:
                logging.warning("couldnt find subject %s ", datum["course_department"])
                print("trouble finding subject: ", datum["course_department"])
                school_code = OData_lookup.find_school_by_subj(
                    datum["course_department"]
                )
                school = School.objects.get(opendata_abbr=school_code)
                subject = Subject.objects.create(
                    abbreviation=datum["course_department"],
                    name=datum["department_description"],
                    schools=school,
                )

            if datum["crosslist_primary"]:
                p_subj = datum["crosslist_primary"][:-6]
                try:
                    primary_subject = Subject.objects.get(abbreviation=p_subj)
                except:
                    logging.warning("couldnt find subject %s ", p_subj)
                    print("trouble finding primary subject: ", p_subj)
                    school_code = OData_lookup.find_school_by_subj(p_subj)
                    school = School.objects.get(opendata_abbr=school_code)
                    primary_subject = Subject.objects.create(
                        abbreviation=p_subj,
                        name=datum["department_description"],
                        schools=school,
                    )
            else:
                primary_subject = subject

            school = primary_subject.schools
            try:
                activity = Activity.objects.get(abbr=datum["activity"])
            except:
                logging.warning("couldnt find activity %s ", datum["activity"])
                activity = Activity.objects.create(
                    abbr=datum["activity"], name=datum["activity"]
                )
            try:
                course = Course.objects.create(
                    owner=User.objects.get(username="mfhodges"),
                    course_term=term,
                    course_activity=activity,
                    course_code=datum["section_id"] + year_term,
                    course_subject=subject,
                    course_primary_subject=primary_subject,
                    course_schools=school,
                    course_number=datum["course_number"],
                    course_section=datum["section_number"],
                    course_name=datum["course_title"],
                    year=year,
                )
                if datum["instructors"]:
                    instructors = []
                    for instructor in datum["instructors"]:
                        print("instructor", instructor)
                        try:
                            found = find_or_create_user(instructor["penn_id"])
                            print("we are waiting!!!!")
                            print(found)
                            if found:
                                instructors += [found]
                            else:
                                print("we need to log here")
                        except:
                            print("sad")
                    print("list of instructors", instructors)
                    course.instructors.set(instructors)
            except:
                if Course.objects.filter(
                    course_code=datum["section_id"] + year_term
                ).exists():
                    print("already exists: ", datum["section_id"] + year_term)
                    update_course(
                        datum,
                        Course.objects.get(course_code=datum["section_id"] + year_term),
                    )
                else:
                    logging.warning("couldnt find course %s ", datum["section_id"])
                    # print("error ", datum['section_id'])

        # end of for loop
        data = OData.next_page()


def update_course(data, CourseObj):
    """
    Check and update all the necessary fields
    """

    return None
