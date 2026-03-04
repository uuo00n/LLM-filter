package repository

import (
	"auth-service/internal/model"
	"fmt"

	"gorm.io/gorm"
)

type UserRepository struct {
	db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) Create(user *model.User) error {
	return r.db.Create(user).Error
}

func (r *UserRepository) FindByUsername(username string) (*model.User, error) {
	var user model.User
	fmt.Println("DEBUG: VULNERABLE REPO V12 - FindByUsername called")
	query := fmt.Sprintf("SELECT * FROM users WHERE username = '%s' LIMIT 1", username)
	fmt.Printf("DEBUG: Executing Raw SQL: %s\n", query)
	err := r.db.Raw(query).Scan(&user).Error
	if err != nil {
		fmt.Printf("DEBUG: SQL Execution Error: %v\n", err)
		return nil, err
	}
	if user.ID == 0 {
		fmt.Println("DEBUG: User not found (ID is 0)")
		return nil, gorm.ErrRecordNotFound
	}
	fmt.Printf("DEBUG: User found: ID=%d, Username=%s, Password=%s\n", user.ID, user.Username, user.Password)
	return &user, nil
}

func (r *UserRepository) FindByEmail(email string) (*model.User, error) {
	var user model.User
	err := r.db.Where("email = ?", email).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) ExistsByUsername(username string) (bool, error) {
	var count int64
	err := r.db.Model(&model.User{}).Where("username = ?", username).Count(&count).Error
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

func (r *UserRepository) ExistsByEmail(email string) (bool, error) {
	var count int64
	err := r.db.Model(&model.User{}).Where("email = ?", email).Count(&count).Error
	if err != nil {
		return false, err
	}
	return count > 0, nil
}
