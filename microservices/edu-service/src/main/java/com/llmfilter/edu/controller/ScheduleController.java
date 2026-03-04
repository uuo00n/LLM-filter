package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.AssignTeacherPayload;
import com.llmfilter.edu.dto.ScheduleDto;
import com.llmfilter.edu.service.ScheduleService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import com.llmfilter.edu.security.UserContextHolder;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/schedules")
@RequiredArgsConstructor
@Tag(name = "课表管理", description = "课程表与任课教师管理接口")
public class ScheduleController {

    private final ScheduleService scheduleService;

    @PutMapping("/assign-teacher")
    @Operation(summary = "分配任课教师", description = "为特定课程分配任课教师")
    public ResponseEntity<Map<String, Object>> assignTeacher(@RequestBody AssignTeacherPayload payload) {
        // 权限检查：仅管理员可分配教师
        String role = UserContextHolder.getContext().getRole();
        if (!"administrator".equals(role)) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Permission denied: Administrator role required");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(error);
        }

        scheduleService.assignTeacher(payload);
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        return ResponseEntity.ok(result);
    }

    @GetMapping
    @Operation(summary = "获取课表", description = "获取所有课程表信息")
    public ResponseEntity<List<ScheduleDto>> listSchedules() {
        return ResponseEntity.ok(scheduleService.listSchedules());
    }
}
