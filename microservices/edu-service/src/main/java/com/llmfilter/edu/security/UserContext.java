package com.llmfilter.edu.security;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserContext {
    private Long userId;
    private String username;
    private String role;
    private String personId;
    private String personType;
    private String edition;
    private Integer roleLevel;
}
