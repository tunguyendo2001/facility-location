package com.retaildss.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.io.BufferedReader;
import java.io.InputStreamReader;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisService {
    
    @Value("${python.script.path:mcdm/topsis.py}")
    private String pythonScriptPath;
    
    @Value("${python.executable:python3}")
    private String pythonExecutable;
    
    /**
     * Chạy Python script để thực hiện phân tích TOPSIS
     * @return Kết quả output từ Python script
     */
    public String runTopsisAnalysis() {
        try {
            log.info("Starting TOPSIS analysis...");
            
            // Tạo ProcessBuilder để chạy Python script
            ProcessBuilder processBuilder = new ProcessBuilder(
                pythonExecutable,
                pythonScriptPath
            );
            
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();
            
            // Đọc output từ Python script
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                    log.info("Python output: {}", line);
                }
            }
            
            // Đợi process kết thúc
            int exitCode = process.waitFor();
            log.info("Python script finished with exit code: {}", exitCode);
            
            if (exitCode != 0) {
                String errorMsg = "TOPSIS analysis failed with exit code: " + exitCode;
                log.error(errorMsg);
                throw new RuntimeException(errorMsg);
            }
            
            return output.toString();
            
        } catch (Exception e) {
            log.error("Error running TOPSIS analysis", e);
            throw new RuntimeException("Failed to execute TOPSIS analysis: " + e.getMessage(), e);
        }
    }
}
