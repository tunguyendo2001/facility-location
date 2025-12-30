package com.retaildss.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.retaildss.dto.TopSiteDto;
import com.retaildss.entity.PotentialSite;
import com.retaildss.repository.PotentialSiteRepository;
import com.retaildss.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class AnalysisController {
    
    private final AnalysisService analysisService;
    private final PotentialSiteRepository siteRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    /**
     * Run MCDM analysis (default: TOPSIS)
     * GET /api/analysis/run?algorithm=topsis&configId=1&topN=10
     */
    @GetMapping("/run")
    public ResponseEntity<?> runAnalysis(
            @RequestParam(required = false, defaultValue = "topsis") String algorithm,
            @RequestParam(required = false) Long configId,
            @RequestParam(required = false, defaultValue = "10") Integer topN) {
        try {
            log.info("Received request to run {} analysis", algorithm.toUpperCase());
            
            // Call Flask MCDM service
            String mcdmResponse = analysisService.runMcdmAnalysis(algorithm, configId, topN);
            
            // Parse JSON response
            JsonNode jsonResponse = objectMapper.readTree(mcdmResponse);
            
            // Return response directly from MCDM service
            return ResponseEntity.ok(jsonResponse);
            
        } catch (Exception e) {
            log.error("Error in analysis endpoint", e);
            return ResponseEntity.status(500)
                .body(Map.of(
                    "success", false,
                    "error", "Analysis failed: " + e.getMessage(),
                    "timestamp", LocalDateTime.now()
                ));
        }
    }
    
    /**
     * Run specific algorithm analysis
     * POST /api/analysis/topsis
     * POST /api/analysis/ahp
     */
    @PostMapping("/{algorithm}")
    public ResponseEntity<?> runSpecificAnalysis(
            @PathVariable String algorithm,
            @RequestParam(required = false) Long configId,
            @RequestParam(required = false, defaultValue = "10") Integer topN) {
        
        return runAnalysis(algorithm, configId, topN);
    }
    
    /**
     * Get list of supported algorithms
     * GET /api/analysis/algorithms
     */
    @GetMapping("/algorithms")
    public ResponseEntity<?> getSupportedAlgorithms() {
        try {
            String algorithms = analysisService.getSupportedAlgorithms();
            JsonNode jsonResponse = objectMapper.readTree(algorithms);
            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            log.error("Error getting algorithms", e);
            return ResponseEntity.status(500)
                .body(Map.of("error", "Failed to get algorithms: " + e.getMessage()));
        }
    }
    
    /**
     * API để lấy danh sách top địa điểm tốt nhất (từ database)
     * GET /api/analysis/top-sites?limit=10
     */
    @GetMapping("/top-sites")
    public ResponseEntity<List<TopSiteDto>> getTopSites(
            @RequestParam(defaultValue = "10") int limit) {
        try {
            List<PotentialSite> sites = siteRepository.findTopSites();
            
            List<TopSiteDto> result = sites.stream()
                .limit(limit)
                .map(site -> new TopSiteDto(
                    site.getId(),
                    site.getSiteCode(),
                    site.getAddress(),
                    site.getDistrict().getName(),
                    site.getTopsisScore(),
                    site.getRankPosition(),
                    site.getRentCost(),
                    site.getFloorArea(),
                    site.getTrafficScore(),
                    site.getCompetitorCount()
                ))
                .collect(Collectors.toList());
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            log.error("Error fetching top sites", e);
            return ResponseEntity.status(500).build();
        }
    }
    
    /**
     * Health check
     * GET /api/analysis/health
     */
    @GetMapping("/health")
    public ResponseEntity<?> healthCheck() {
        boolean mcdmHealthy = analysisService.checkMcdmServiceHealth();
        
        return ResponseEntity.ok(Map.of(
            "status", "running",
            "service", "Retail DSS Analysis Service",
            "mcdm_service_healthy", mcdmHealthy,
            "timestamp", LocalDateTime.now()
        ));
    }
}
