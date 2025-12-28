package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.*;
import com.llmfilter.edu.security.UserContext;
import com.llmfilter.edu.security.UserContextHolder;
import com.llmfilter.edu.service.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/dashboard")
@RequiredArgsConstructor
@Tag(name = "Dashboard", description = "仪表盘数据接口")
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping("/student/today")
    @Operation(summary = "学生今日概览", description = "获取当前学生用户的今日课程、出勤状态及待办事项等概览信息")
    public StudentTodaySummary getStudentToday() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getStudentTodaySummary(user);
    }

    @GetMapping("/student/week")
    @Operation(summary = "学生周课表", description = "获取当前学生用户的周课表信息，支持指定周次（默认当前周）")
    public StudentWeekSummary getStudentWeek(@RequestParam(required = false) Integer week) {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getStudentWeekSchedule(user, week);
    }

    @GetMapping("/teacher/week")
    @Operation(summary = "教师周课表", description = "获取当前教师用户的周课表信息，支持指定周次（默认当前周）")
    public TeacherWeekSummary getTeacherWeek(@RequestParam(required = false) Integer week) {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getTeacherWeekSchedule(user, week);
    }

    @GetMapping("/homeroom/current")
    @Operation(summary = "班主任当前概览", description = "获取班主任所管理班级的当前出勤、请假及课堂状态信息")
    public HomeroomCurrentSummary getHomeroomCurrent() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getHomeroomCurrentSummary(user);
    }

    @GetMapping("/department/overview")
    @Operation(summary = "部门概览", description = "获取部门管理人员的部门整体出勤、教学活动及异常情况概览")
    public DepartmentOverview getDepartmentOverview() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getDepartmentOverview(user);
    }

    @GetMapping("/campus/overview")
    @Operation(summary = "校园概览", description = "获取校级管理人员的全校出勤率、课堂活跃度及安全预警概览")
    public CampusOverview getCampusOverview() {
        UserContext user = UserContextHolder.getContext();
        return dashboardService.getCampusOverview(user);
    }
}
