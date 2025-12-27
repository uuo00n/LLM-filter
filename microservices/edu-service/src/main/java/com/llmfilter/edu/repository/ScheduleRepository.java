package com.llmfilter.edu.repository;

import com.llmfilter.edu.model.Schedule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ScheduleRepository extends JpaRepository<Schedule, Long> {
    Optional<Schedule> findByLessonId(String lessonId);
    List<Schedule> findAllByOrderByWeekdayAscPeriodAsc();
}
