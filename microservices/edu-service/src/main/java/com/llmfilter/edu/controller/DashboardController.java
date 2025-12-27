package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.*;
import com.llmfilter.edu.security.UserContext;
import com.llmfilter.edu.security.UserContextHolder;
import com.llmfilter.edu.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping("/student/today")
    public StudentTodaySummary getStudentToday() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getStudentTodaySummary(user);
    }

    @GetMapping("/student/week")
    public StudentWeekSummary getStudentWeek(@RequestParam(required = false) Integer week) {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getStudentWeekSchedule(user, week);
    }

    @GetMapping("/teacher/week")
    public TeacherWeekSummary getTeacherWeek(@RequestParam(required = false) Integer week) {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getTeacherWeekSchedule(user, week);
    }

    @GetMapping("/homeroom/current")
    public HomeroomCurrentSummary getHomeroomCurrent() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getHomeroomCurrentSummary(user);
    }

    @GetMapping("/department/overview")
    public DepartmentOverview getDepartmentOverview() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getDepartmentOverview(user);
    }

    @GetMapping("/campus/overview")
    public CampusOverview getCampusOverview() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getCampusOverview(user);
    }
}
