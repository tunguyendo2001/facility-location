package com.retaildss.controller;

import com.retaildss.dto.SiteStatisticsDto;
import com.retaildss.entity.PotentialSite;
import com.retaildss.service.SiteService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/sites")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class SiteController {
    
    private final SiteService siteService;
    
    @GetMapping
    public ResponseEntity<List<PotentialSite>> getAllActiveSites() {
        log.info("Fetching all active sites");
        List<PotentialSite> sites = siteService.getAllActiveSites();
        return ResponseEntity.ok(sites);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<PotentialSite> getSiteById(@PathVariable Long id) {
        log.info("Fetching site with id: {}", id);
        PotentialSite site = siteService.getSiteById(id);
        return ResponseEntity.ok(site);
    }
    
    @GetMapping("/statistics")
    public ResponseEntity<SiteStatisticsDto> getStatistics() {
        log.info("Fetching site statistics");
        SiteStatisticsDto stats = siteService.getStatistics();
        return ResponseEntity.ok(stats);
    }
}
