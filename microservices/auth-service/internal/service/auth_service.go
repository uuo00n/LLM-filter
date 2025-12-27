package service

import (
	"auth-service/internal/model"
	"auth-service/internal/repository"
	"auth-service/pkg/utils"
	"errors"
)

type AuthService struct {
	repo *repository.UserRepository
}

func NewAuthService(repo *repository.UserRepository) *AuthService {
	return &AuthService{repo: repo}
}

// RegisterRequest 注册请求参数
type RegisterRequest struct {
	Username string
	Email    string
	Password string
}

// LoginRequest 登录请求参数
type LoginRequest struct {
	Username string
	Password string
}

// Register 用户注册业务逻辑
func (s *AuthService) Register(req *RegisterRequest) (*model.User, error) {
	// 检查用户名是否存在
	exists, err := s.repo.ExistsByUsername(req.Username)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, errors.New("username already exists")
	}

	// 检查邮箱是否存在
	exists, err = s.repo.ExistsByEmail(req.Email)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, errors.New("email already registered")
	}

	// 密码加密
	hashedPwd, err := utils.HashPassword(req.Password)
	if err != nil {
		return nil, err
	}

	// 创建用户
	user := &model.User{
		Username: req.Username,
		Email:    req.Email,
		Password: hashedPwd,
		Role:     "user",
		Edition:  "edu",
	}

	if err := s.repo.Create(user); err != nil {
		return nil, err
	}

	return user, nil
}

// Login 用户登录业务逻辑
func (s *AuthService) Login(req *LoginRequest) (string, *model.User, error) {
	user, err := s.repo.FindByUsername(req.Username)
	if err != nil {
		return "", nil, errors.New("invalid username or password")
	}

	if !utils.CheckPasswordHash(req.Password, user.Password) {
		return "", nil, errors.New("invalid username or password")
	}

	token, err := utils.GenerateToken(user.ID, user.Username, user.Role)
	if err != nil {
		return "", nil, err
	}

	return token, user, nil
}
