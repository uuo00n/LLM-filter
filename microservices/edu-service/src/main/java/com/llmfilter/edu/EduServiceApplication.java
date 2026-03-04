package com.llmfilter.edu;

import com.llmfilter.edu.security.JwtAuthenticationFilter;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@EnableCaching
@OpenAPIDefinition(
    info = @Info(
        title = "Edu Service API",
        version = "1.0",
        description = "LLM 过滤系统 - 教务核心服务 API"
    )
)
public class EduServiceApplication {

	public static void main(String[] args) {
		// 尝试加载根目录 .env 文件 (用于本地开发)
		// 注意：生产环境 Docker 会直接注入环境变量，这里仅作为本地开发辅助
		// Spring Boot 默认不加载 .env，这里使用 System.setProperty 模拟或推荐使用插件
		// 为了简单起见，这里不做复杂的 .env 解析，建议本地开发使用 IDE 插件或手动设置环境变量
		// 或者使用 java-dotenv 库
		
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
