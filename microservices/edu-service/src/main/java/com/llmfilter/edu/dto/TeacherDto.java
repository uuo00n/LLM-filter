package com.llmfilter.edu.dto;

import lombok.Data;
import java.util.List;

@Data
public class TeacherDto {
    private String personId;
    private String teacherId;
    private String department;
    private List<String> roles;
    private String accountId;
}
