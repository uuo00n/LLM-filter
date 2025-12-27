package com.llmfilter.edu.service;

import com.llmfilter.edu.dto.PersonDto;
import com.llmfilter.edu.model.Person;
import com.llmfilter.edu.repository.PersonRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PersonService {

    private final PersonRepository personRepository;

    @Transactional
    public int bulkCreate(List<PersonDto> persons) {
        List<Person> entities = persons.stream()
                .map(dto -> Person.builder()
                        .personId(dto.getPersonId())
                        .name(dto.getName())
                        .type(dto.getType())
                        .build())
                .collect(Collectors.toList());
        return personRepository.saveAll(entities).size();
    }

    @Transactional(readOnly = true)
    public Map<String, Object> listPersons() {
        List<Person> all = personRepository.findAll();
        
        List<PersonDto> items = all.stream()
                .map(p -> {
                    PersonDto dto = new PersonDto();
                    dto.setPersonId(p.getPersonId());
                    dto.setName(p.getName());
                    dto.setType(p.getType());
                    return dto;
                })
                .collect(Collectors.toList());

        Map<String, Long> counts = all.stream()
                .collect(Collectors.groupingBy(Person::getType, Collectors.counting()));

        Map<String, Object> result = new HashMap<>();
        result.put("items", items);
        result.put("counts_by_type", counts);
        return result;
    }
}
