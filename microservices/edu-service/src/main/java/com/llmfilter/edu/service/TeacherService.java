package com.llmfilter.edu.service;

import com.llmfilter.edu.dto.TeacherDto;
import com.llmfilter.edu.model.Teacher;
import com.llmfilter.edu.repository.TeacherRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TeacherService {

    private final TeacherRepository teacherRepository;

    @Transactional
    public int bulkCreate(List<TeacherDto> teachers) {
        List<Teacher> entities = teachers.stream()
                .map(dto -> Teacher.builder()
                        .personId(dto.getPersonId())
                        .teacherId(dto.getTeacherId())
                        .department(dto.getDepartment())
                        .roles(String.join(",", dto.getRoles()))
                        .accountId(dto.getAccountId())
                        .build())
                .collect(Collectors.toList());
        return teacherRepository.saveAll(entities).size();
    }

    @Transactional(readOnly = true)
    public List<TeacherDto> listTeachers() {
        return teacherRepository.findAll().stream()
                .map(t -> {
                    TeacherDto dto = new TeacherDto();
                    dto.setPersonId(t.getPersonId());
                    dto.setTeacherId(t.getTeacherId());
                    dto.setDepartment(t.getDepartment());
                    dto.setRoles(t.getRoles() != null ? Arrays.asList(t.getRoles().split(",")) : Collections.emptyList());
                    dto.setAccountId(t.getAccountId());
                    return dto;
                })
                .collect(Collectors.toList());
    }
}
