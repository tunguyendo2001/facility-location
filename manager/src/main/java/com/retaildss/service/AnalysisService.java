package com.retaildss.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisService {
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    @Value("${mcdm.service.url:http://localhost:5000}")
    private String mcdmServiceUrl;
    
    @Value("${mcdm.service.default-algorithm:topsis}")
    private String defaultAlgorithm;
    
    /**
     * Chạy phân tích MCDM bằng cách gọi Flask service
     * 
     * @param algorithm Algorithm name (topsis, ahp, etc.)
     * @param configId Configuration ID (null = use active config)
     * @param topN Number of top results to return
     * @return JSON response từ Flask service
     */
    public String runMcdmAnalysis(String algorithm, Long configId, Integer topN) {
        try {
            log.info("Calling MCDM service: algorithm={}, configId={}, topN={}", 
                     algorithm, configId, topN);
            
            // Prepare request body
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("algorithm", algorithm != null ? algorithm : defaultAlgorithm);
            if (configId != null) {
                requestBody.put("config_id", configId);
            }
            if (topN != null) {
                requestBody.put("top_n", topN);
            }
            
            // Set headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create request entity
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
            
            // Call Flask API
            String url = mcdmServiceUrl + "/api/analyze";
            log.info("Sending POST request to: {}", url);
            
            ResponseEntity<String> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                requestEntity,
                String.class
            );
            
            if (response.getStatusCode().is2xxSuccessful()) {
                log.info("MCDM analysis completed successfully");
                return response.getBody();
            } else {
                String errorMsg = "MCDM service returned error: " + response.getStatusCode();
                log.error(errorMsg);
                throw new RuntimeException(errorMsg);
            }
            
        } catch (Exception e) {
            log.error("Error calling MCDM service", e);
            throw new RuntimeException("Failed to execute MCDM analysis: " + e.getMessage(), e);
        }
    }
    
    /**
     * Convenience method - use default parameters
     */
    public String runTopsisAnalysis() {
        return runMcdmAnalysis("topsis", null, 10);
    }
    
    /**
     * Check MCDM service health
     */
    public boolean checkMcdmServiceHealth() {
        try {
            String url = mcdmServiceUrl + "/api/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.error("MCDM service health check failed", e);
            return false;
        }
    }
    
    /**
     * Get supported algorithms from MCDM service
     */
    public String getSupportedAlgorithms() {
        try {
            String url = mcdmServiceUrl + "/api/algorithms";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to get algorithms list");
            }
        } catch (Exception e) {
            log.error("Error getting algorithms list", e);
            throw new RuntimeException("Failed to get algorithms list: " + e.getMessage(), e);
        }
    }
}
