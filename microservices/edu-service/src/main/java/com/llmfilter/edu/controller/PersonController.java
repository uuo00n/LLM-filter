package com.llmfilter.edu.controller;

import com.llmfilter.edu.dto.PersonDto;
import com.llmfilter.edu.service.PersonService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/persons")
@RequiredArgsConstructor
@Tag(name = "人员管理", description = "基础人员信息管理接口")
public class PersonController {

    private final PersonService personService;

    @PostMapping("/bulk")
    @Operation(summary = "批量创建人员", description = "批量导入或创建人员基础信息")
    public ResponseEntity<Map<String, Integer>> bulkCreate(@RequestBody List<PersonDto> persons) {
        int count = personService.bulkCreate(persons);
        Map<String, Integer> result = new HashMap<>();
        result.put("inserted", count);
        return ResponseEntity.ok(result);
    }

    @GetMapping
    @Operation(summary = "获取人员列表", description = "获取所有人员信息")
    public ResponseEntity<Map<String, Object>> listPersons() {
        return ResponseEntity.ok(personService.listPersons());
    }
}
