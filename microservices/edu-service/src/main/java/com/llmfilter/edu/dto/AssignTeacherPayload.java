package com.llmfilter.edu.dto;

import lombok.Data;

@Data
public class AssignTeacherPayload {
    private String lessonId;
    private String teacherPersonId;
}
