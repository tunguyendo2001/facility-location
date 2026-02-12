package com.retaildss.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.retaildss.dto.TopSiteDto;
import com.retaildss.entity.EvaluationResult;
import com.retaildss.service.AnalysisService;
import com.retaildss.service.EvaluationResultService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class AnalysisController {

    private final AnalysisService analysisService;
    private final EvaluationResultService evaluationResultService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Run MCDM analysis (default: TOPSIS)
     * POST /api/analysis/run?algorithm=topsis&configId=1&userId=1&topN=10
     */
    @PostMapping("/run")
    public ResponseEntity<?> runAnalysis(
            @RequestParam(required = false, defaultValue = "topsis") String algorithm,
            @RequestParam(required = false) Long configId,
            @RequestParam(required = false) Long userId,
            @RequestParam(required = false, defaultValue = "10") Integer topN) {
        try {
            log.info("Received request to run {} analysis", algorithm.toUpperCase());

            // Call Flask MCDM service
            String mcdmResponse = analysisService.runMcdmAnalysis(algorithm, configId, userId, topN);

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
                            "timestamp", LocalDateTime.now()));
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
            @RequestParam(required = false) Long userId,
            @RequestParam(required = false, defaultValue = "10") Integer topN) {

        return runAnalysis(algorithm, configId, userId, topN);
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
     * Get top sites from latest batch
     * GET /api/analysis/top-sites?limit=10
     */
    @GetMapping("/top-sites")
    public ResponseEntity<List<TopSiteDto>> getTopSites(
            @RequestParam(defaultValue = "10") int limit) {
        try {
            List<TopSiteDto> result = evaluationResultService.getTopSitesFromLatestBatch(limit);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            log.error("Error fetching top sites", e);
            return ResponseEntity.status(500).build();
        }
    }

    /**
     * Get evaluation history for a specific site
     * GET /api/analysis/site/{siteId}/history
     */
    @GetMapping("/site/{siteId}/history")
    public ResponseEntity<?> getSiteEvaluationHistory(@PathVariable Long siteId) {
        try {
            List<EvaluationResult> history = evaluationResultService.getEvaluationHistoryBySite(siteId);
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "site_id", siteId,
                    "total_evaluations", history.size(),
                    "history", history));
        } catch (Exception e) {
            log.error("Error fetching evaluation history", e);
            return ResponseEntity.status(500)
                    .body(Map.of("success", false, "error", e.getMessage()));
        }
    }

    /**
     * Get results from latest batch (via Flask)
     * GET /api/analysis/results/latest?limit=10
     */
    @GetMapping("/results/latest")
    public ResponseEntity<?> getLatestBatchResults(
            @RequestParam(defaultValue = "10") int limit) {
        try {
            String response = analysisService.getLatestBatchResults(limit);
            JsonNode jsonResponse = objectMapper.readTree(response);
            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            log.error("Error getting latest batch results", e);
            return ResponseEntity.status(500)
                    .body(Map.of("success", false, "error", e.getMessage()));
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
                "timestamp", LocalDateTime.now()));
    }
}
