package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.ClassDto;
import com.llmfilter.edu.dto.HeadTeacherPayload;
import com.llmfilter.edu.service.ClassService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/classes")
@RequiredArgsConstructor
@Tag(name = "班级管理", description = "班级与班主任管理接口")
public class ClassController {

    private final ClassService classService;

    @GetMapping
    @Operation(summary = "获取班级列表", description = "获取所有班级的基础信息")
    public ResponseEntity<List<ClassDto>> listClasses() {
        return ResponseEntity.ok(classService.listClasses());
    }

    @PutMapping("/{classId}/head-teacher")
    @Operation(summary = "设置班主任", description = "为指定班级分配或更新班主任")
    public ResponseEntity<Map<String, Boolean>> setHeadTeacher(
            @PathVariable String classId,
            @RequestBody HeadTeacherPayload payload) {
        classService.setHeadTeacher(classId, payload);
        Map<String, Boolean> result = new HashMap<>();
        result.put("success", true);
        return ResponseEntity.ok(result);
    }
}
