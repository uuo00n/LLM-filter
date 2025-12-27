package model

import (
	"time"

	"gorm.io/gorm"
)

type Binding struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	UserID    uint           `gorm:"index;not null" json:"user_id"` // 对应 account_id
	PersonID  string         `gorm:"index;not null" json:"person_id"`
	Type      string         `gorm:"type:varchar(20);not null" json:"type"` // student, teacher, staff
	Primary   bool           `gorm:"default:false" json:"primary"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}
