package com.llmfilter.edu.service;

import com.llmfilter.edu.dto.*;
import com.llmfilter.edu.security.UserContext;

public interface DashboardService {
    StudentTodaySummary getStudentTodaySummary(UserContext user);
    StudentWeekSummary getStudentWeekSchedule(UserContext user, Integer week);
    TeacherWeekSummary getTeacherWeekSchedule(UserContext user, Integer week);
    HomeroomCurrentSummary getHomeroomCurrentSummary(UserContext user);
    DepartmentOverview getDepartmentOverview(UserContext user);
    CampusOverview getCampusOverview(UserContext user);
}
