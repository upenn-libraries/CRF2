import api

# https://canvas.upenn.edu/courses/1448756
# bad link testing

# https://canvas.upenn.edu/courses/1422332
# adv span

print("api.get_course(1448756)\n\t", api.get_course(1448756))
print(
    "api.get_course_users(1448756)\n\t", api.get_course_users(1448756)
)  # no teachers so should get error


print("api.get_course(1422332)\n\t", api.get_course(1422332))
print(
    "api.get_course_users(1422332)\n\t", api.get_course_users(1422332)
)  # no teachers so should get error
