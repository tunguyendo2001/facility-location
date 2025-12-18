package com.retaildss.controller;

import com.retaildss.entity.District;
import com.retaildss.service.DistrictService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/districts")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class DistrictController {
    
    private final DistrictService districtService;
    
    @GetMapping
    public ResponseEntity<List<District>> getAllDistricts() {
        log.info("Fetching all districts");
        List<District> districts = districtService.getAllDistricts();
        return ResponseEntity.ok(districts);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<District> getDistrictById(@PathVariable Long id) {
        log.info("Fetching district with id: {}", id);
        District district = districtService.getDistrictById(id);
        return ResponseEntity.ok(district);
    }
}
