package com.llmfilter.edu.service;

import com.llmfilter.edu.dto.ClassDto;
import com.llmfilter.edu.dto.HeadTeacherPayload;
import com.llmfilter.edu.model.ClassEntity;
import com.llmfilter.edu.repository.ClassRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.persistence.EntityNotFoundException;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ClassService {

    private final ClassRepository classRepository;

    @Transactional(readOnly = true)
    public List<ClassDto> listClasses() {
        return classRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public void setHeadTeacher(String classId, HeadTeacherPayload payload) {
        ClassEntity clazz = classRepository.findByClassId(classId)
                .orElseThrow(() -> new EntityNotFoundException("Class not found: " + classId));
        
        clazz.setHeadTeacherPersonId(payload.getHeadTeacherPersonId());
        classRepository.save(clazz);
    }

    private ClassDto mapToDto(ClassEntity entity) {
        ClassDto dto = new ClassDto();
        dto.setId(entity.getId());
        dto.setClassId(entity.getClassId());
        dto.setHeadTeacherPersonId(entity.getHeadTeacherPersonId());
        dto.setGrade(entity.getGrade());
        // TODO: Calculate students count
        dto.setStudentsCount(0);
        return dto;
    }
}
