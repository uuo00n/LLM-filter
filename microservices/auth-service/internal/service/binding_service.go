package service

import (
	"auth-service/internal/model"
	"auth-service/internal/repository"
	"errors"
)

type BindingService struct {
	repo *repository.BindingRepository
}

func NewBindingService(repo *repository.BindingRepository) *BindingService {
	return &BindingService{repo: repo}
}

type CreateBindingRequest struct {
	UserID   uint
	PersonID string
	Type     string
	Primary  bool
}

// CreateBinding 创建绑定
func (s *BindingService) CreateBinding(req *CreateBindingRequest) error {
	// 如果是主绑定，检查是否已存在同类型的主绑定
	if req.Primary {
		exists, err := s.repo.ExistsPrimary(req.UserID, req.Type)
		if err != nil {
			return err
		}
		if exists {
			return errors.New("primary binding of this type already exists")
		}
	}

	binding := &model.Binding{
		UserID:   req.UserID,
		PersonID: req.PersonID,
		Type:     req.Type,
		Primary:  req.Primary,
	}

	return s.repo.Create(binding)
}

// Unbind 删除绑定
func (s *BindingService) Unbind(userID uint, personID string) error {
	// TODO: 可以在这里检查是否存在，或者直接删除（幂等）
	// GORM 的 Delete 如果没找到记录不会报错，只会返回 RowsAffected=0
	// 这里简单直接调用 Delete
	return s.repo.Delete(userID, personID)
}

// GetPrimaryBinding 获取用户的主绑定
func (s *BindingService) GetPrimaryBinding(userID uint) (*model.Binding, error) {
	return s.repo.FindPrimaryByUserID(userID)
}
