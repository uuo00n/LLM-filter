package com.llmfilter.edu;

import com.llmfilter.edu.security.JwtAuthenticationFilter;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@OpenAPIDefinition(
    info = @Info(
        title = "Edu Service API",
        version = "1.0",
        description = "LLM 过滤系统 - 教务核心服务 API"
    )
)
public class EduServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(EduServiceApplication.class, args);
	}

	@Bean
	public FilterRegistrationBean<JwtAuthenticationFilter> loggingFilter(JwtAuthenticationFilter filter) {
		FilterRegistrationBean<JwtAuthenticationFilter> registrationBean = new FilterRegistrationBean<>();
		registrationBean.setFilter(filter);
		registrationBean.addUrlPatterns("/api/v1/*"); // 拦截 API 接口
		registrationBean.setOrder(1);
		return registrationBean;
	}
}
