package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.TeacherDto;
import com.llmfilter.edu.service.TeacherService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/teachers")
@RequiredArgsConstructor
@Tag(name = "教师管理", description = "教师信息管理接口")
public class TeacherController {

    private final TeacherService teacherService;

    @PostMapping("/bulk")
    @Operation(summary = "批量创建教师", description = "批量导入或创建教师信息")
    public ResponseEntity<Map<String, Integer>> bulkCreate(@RequestBody List<TeacherDto> teachers) {
        int count = teacherService.bulkCreate(teachers);
        Map<String, Integer> result = new HashMap<>();
        result.put("inserted", count);
        return ResponseEntity.ok(result);
    }

    @GetMapping
    @Operation(summary = "获取教师列表", description = "获取所有教师信息")
    public ResponseEntity<List<TeacherDto>> listTeachers() {
        return ResponseEntity.ok(teacherService.listTeachers());
    }
}
