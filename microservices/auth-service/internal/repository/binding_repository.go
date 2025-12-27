package repository

import (
	"auth-service/internal/model"

	"gorm.io/gorm"
)

type BindingRepository struct {
	db *gorm.DB
}

func NewBindingRepository(db *gorm.DB) *BindingRepository {
	return &BindingRepository{db: db}
}

// Create 创建绑定
func (r *BindingRepository) Create(binding *model.Binding) error {
	return r.db.Create(binding).Error
}

// Delete 删除绑定
func (r *BindingRepository) Delete(userID uint, personID string) error {
	return r.db.Where("user_id = ? AND person_id = ?", userID, personID).Delete(&model.Binding{}).Error
}

// FindPrimaryByUserID 查找用户的主绑定
func (r *BindingRepository) FindPrimaryByUserID(userID uint) (*model.Binding, error) {
	var binding model.Binding
	err := r.db.Where("user_id = ? AND \"primary\" = ?", userID, true).First(&binding).Error
	if err != nil {
		return nil, err
	}
	return &binding, nil
}

// FindPrimaryByUserIDAndType 查找用户指定类型的主绑定
func (r *BindingRepository) FindPrimaryByUserIDAndType(userID uint, bindingType string) (*model.Binding, error) {
	var binding model.Binding
	err := r.db.Where("user_id = ? AND type = ? AND \"primary\" = ?", userID, bindingType, true).First(&binding).Error
	if err != nil {
		return nil, err
	}
	return &binding, nil
}

// ExistsPrimary 检查是否存在主绑定
func (r *BindingRepository) ExistsPrimary(userID uint, bindingType string) (bool, error) {
	var count int64
	err := r.db.Model(&model.Binding{}).
		Where("user_id = ? AND type = ? AND \"primary\" = ?", userID, bindingType, true).
		Count(&count).Error
	if err != nil {
		return false, err
	}
	return count > 0, nil
}
