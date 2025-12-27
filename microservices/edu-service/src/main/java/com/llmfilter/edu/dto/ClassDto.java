package com.llmfilter.edu.dto;

import lombok.Data;

@Data
public class ClassDto {
    private Long id;
    private String classId;
    private String headTeacherPersonId;
    private Integer grade;
    private Integer studentsCount;
}
