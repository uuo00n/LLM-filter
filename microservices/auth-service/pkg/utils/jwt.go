package utils

import (
	"fmt"
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

var jwtSecret []byte

func init() {
	secret := os.Getenv("JWT_SECRET")
	if secret == "" {
		log.Fatal("JWT_SECRET environment variable is required")
	}
	if len(secret) < 32 {
		log.Fatal("JWT_SECRET must be at least 32 characters long")
	}
	jwtSecret = []byte(secret)
}

func GetJWTSecret() []byte {
	return jwtSecret
}

// HashPassword 密码加密
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}

// CheckPasswordHash 密码校验
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

// GenerateToken 生成 JWT Token
func GenerateToken(userID uint, username string, role string, roleLevel int, edition string, personID string, personType string) (string, error) {
	claims := jwt.MapClaims{
		"sub":         fmt.Sprintf("%d", userID),
		"name":        username,
		"role":        role,
		"role_level":  roleLevel,
		"edition":     edition,
		"person_id":   personID,
		"person_type": personType,
		"exp":         time.Now().Add(time.Hour * 24).Unix(), // 24小时过期
		"iat":         time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}
