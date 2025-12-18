package com.retaildss.service;

import com.retaildss.entity.District;
import com.retaildss.exception.ResourceNotFoundException;
import com.retaildss.repository.DistrictRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class DistrictService {
    
    private final DistrictRepository districtRepository;
    
    public List<District> getAllDistricts() {
        return districtRepository.findAll();
    }
    
    public District getDistrictById(Long id) {
        return districtRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("District", "id", id));
    }
}
