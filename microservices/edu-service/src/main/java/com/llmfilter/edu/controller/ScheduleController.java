package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.AssignTeacherPayload;
import com.llmfilter.edu.dto.ScheduleDto;
import com.llmfilter.edu.service.ScheduleService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
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
    public ResponseEntity<Map<String, Boolean>> assignTeacher(@RequestBody AssignTeacherPayload payload) {
        scheduleService.assignTeacher(payload);
        Map<String, Boolean> result = new HashMap<>();
        result.put("success", true);
        return ResponseEntity.ok(result);
    }

    @GetMapping
    @Operation(summary = "获取课表", description = "获取所有课程表信息")
    public ResponseEntity<List<ScheduleDto>> listSchedules() {
        return ResponseEntity.ok(scheduleService.listSchedules());
    }
}
