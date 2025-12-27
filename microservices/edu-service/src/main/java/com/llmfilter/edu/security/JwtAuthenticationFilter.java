package com.llmfilter.edu.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import javax.annotation.PostConstruct;
import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.Key;

@Slf4j
@Component
public class JwtAuthenticationFilter implements Filter {

    @Value("${jwt.secret:your_secret_key_here}")
    private String jwtSecret;

    private Key key;

    @PostConstruct
    public void init() {
        log.info("Initializing JwtAuthenticationFilter with secret length: {}", jwtSecret != null ? jwtSecret.length() : 0);
        this.key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        String path = httpRequest.getRequestURI();
        log.info("Processing request in JwtAuthenticationFilter: {}", path);

        HttpServletResponse httpResponse = (HttpServletResponse) response;

        // 跳过 Swagger 文档和健康检查接口
        if (isPublicPath(path)) {
            chain.doFilter(request, response);
            return;
        }

        String authHeader = httpRequest.getHeader("Authorization");
        if (StringUtils.hasText(authHeader) && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            try {
                Claims claims = Jwts.parserBuilder()
                        .setSigningKey(key)
                        .build()
                        .parseClaimsJws(token)
                        .getBody();

                Long userId = claims.get("user_id", Long.class);
                // 注意：JWT 中的 user_id 有时是 number 有时是 string，取决于生成逻辑
                // 兼容处理：如果 sub 是 ID 形式，优先使用 sub
                if (userId == null) {
                    try {
                        userId = Long.valueOf(claims.getSubject());
                    } catch (NumberFormatException e) {
                        // sub 不是数字 ID，可能是用户名
                        if (claims.get("user_id") != null) {
                            userId = Long.valueOf(claims.get("user_id").toString());
                        }
                    }
                }
                
                String username = claims.get("name", String.class);
                if (username == null) {
                    username = claims.getSubject();
                }
                
                String role = claims.get("role", String.class);
                String personId = claims.get("person_id", String.class);
                String personType = claims.get("person_type", String.class);
                String edition = claims.get("edition", String.class);
                Integer roleLevel = claims.get("role_level", Integer.class);

                UserContext userContext = UserContext.builder()
                        .userId(userId)
                        .username(username)
                        .role(role)
                        .personId(personId)
                        .personType(personType)
                        .edition(edition)
                        .roleLevel(roleLevel)
                        .build();

                UserContextHolder.setContext(userContext);
                
                chain.doFilter(request, response);
            } catch (JwtException e) {
                log.warn("Invalid JWT token: {}", e.getMessage());
                httpResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                httpResponse.getWriter().write("{\"error\": \"Invalid or expired token\"}");
            } finally {
                UserContextHolder.clear();
            }
        } else {
            // 没有 Token
            httpResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            httpResponse.getWriter().write("{\"error\": \"Missing Authorization header\"}");
        }
    }

    private boolean isPublicPath(String path) {
        return path.startsWith("/swagger-ui") ||
               path.startsWith("/v3/api-docs") ||
               path.startsWith("/api/v1/edu/health");
    }
}
