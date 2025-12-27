package com.llmfilter.edu.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.llmfilter.edu.dto.AssignTeacherPayload;
import com.llmfilter.edu.dto.ScheduleDto;
import com.llmfilter.edu.model.Schedule;
import com.llmfilter.edu.repository.ScheduleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.persistence.EntityNotFoundException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ScheduleService {

    private final ScheduleRepository scheduleRepository;
    private final ObjectMapper objectMapper;

    @Transactional
    public void assignTeacher(AssignTeacherPayload payload) {
        Schedule schedule = scheduleRepository.findByLessonId(payload.getLessonId())
                .orElseThrow(() -> new EntityNotFoundException("Schedule not found: " + payload.getLessonId()));
        
        schedule.setTeacherPersonId(payload.getTeacherPersonId());
        scheduleRepository.save(schedule);
    }

    @Transactional(readOnly = true)
    public List<ScheduleDto> listSchedules() {
        return scheduleRepository.findAllByOrderByWeekdayAscPeriodAsc().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    private ScheduleDto mapToDto(Schedule entity) {
        ScheduleDto dto = new ScheduleDto();
        dto.setLessonId(entity.getLessonId());
        dto.setWeekday(entity.getWeekday());
        dto.setPeriod(entity.getPeriod());
        dto.setCourseName(entity.getCourseName());
        dto.setTeacherPersonId(entity.getTeacherPersonId());
        
        try {
            if (entity.getClassesJson() != null) {
                dto.setClasses(objectMapper.readValue(entity.getClassesJson(), new TypeReference<List<Map<String, Object>>>() {}));
            } else {
                dto.setClasses(Collections.emptyList());
            }
        } catch (JsonProcessingException e) {
            log.error("Failed to parse classes json for schedule {}", entity.getId(), e);
            dto.setClasses(Collections.emptyList());
        }
        
        return dto;
    }
}
