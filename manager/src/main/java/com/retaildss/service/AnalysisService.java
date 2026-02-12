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
     * Run MCDM analysis by calling Flask service
     * Results will be saved to evaluation_result table by Flask service
     */
    public String runMcdmAnalysis(String algorithm, Long configId, Long userId, Integer topN) {
        try {
            log.info("Calling MCDM service: algorithm={}, configId={}, userId={}, topN={}", 
                     algorithm, configId, userId, topN);
            
            // Prepare request body
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("algorithm", algorithm != null ? algorithm : defaultAlgorithm);
            if (configId != null) {
                requestBody.put("config_id", configId);
            }
            if (userId != null) {
                requestBody.put("user_id", userId);
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
     * Get latest batch results from Flask service
     */
    public String getLatestBatchResults(int limit) {
        try {
            String url = mcdmServiceUrl + "/api/results/latest?limit=" + limit;
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to get latest batch results");
            }
        } catch (Exception e) {
            log.error("Error getting latest batch results", e);
            throw new RuntimeException("Failed to get latest batch results: " + e.getMessage(), e);
        }
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
