package com.retaildss.controller;

import com.retaildss.dto.AnalysisResponse;
import com.retaildss.dto.TopSiteDto;
import com.retaildss.entity.PotentialSite;
import com.retaildss.repository.PotentialSiteRepository;
import com.retaildss.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class AnalysisController {
    
    private final AnalysisService analysisService;
    private final PotentialSiteRepository siteRepository;
    
    /**
     * API để chạy phân tích TOPSIS
     * GET /api/analysis/run
     */
    @GetMapping("/run")
    public ResponseEntity<AnalysisResponse> runAnalysis() {
        try {
            log.info("Received request to run TOPSIS analysis");
            
            // Đếm số lượng sites trước khi phân tích
            long siteCount = siteRepository.count();
            log.info("Total sites in database: {}", siteCount);
            
            // Chạy Python script
            String pythonOutput = analysisService.runTopsisAnalysis();
            
            // Refresh dữ liệu để lấy kết quả mới
            List<PotentialSite> analyzedSites = siteRepository.findByStatusOrderByRankPositionAsc("ACTIVE");
            
            return ResponseEntity.ok(AnalysisResponse.success(
                "TOPSIS analysis completed successfully",
                analyzedSites.size(),
                pythonOutput
            ));
            
        } catch (Exception e) {
            log.error("Error in analysis endpoint", e);
            return ResponseEntity.status(500)
                .body(AnalysisResponse.error("Analysis failed: " + e.getMessage()));
        }
    }
    
    /**
     * API để lấy danh sách top địa điểm tốt nhất
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
     * API health check
     * GET /api/analysis/health
     */
    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("Retail DSS Analysis Service is running");
    }
}
