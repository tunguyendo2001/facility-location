package com.retaildss.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AnalysisResponse {
    private boolean success;
    private String message;
    private LocalDateTime timestamp;
    private Integer sitesAnalyzed;
    private String pythonOutput;
    
    public static AnalysisResponse success(String message, Integer sitesAnalyzed, String pythonOutput) {
        return new AnalysisResponse(
            true, 
            message, 
            LocalDateTime.now(), 
            sitesAnalyzed, 
            pythonOutput
        );
    }
    
    public static AnalysisResponse error(String message) {
        return new AnalysisResponse(
            false, 
            message, 
            LocalDateTime.now(), 
            null, 
            null
        );
    }
}
