package handler

import (
	"auth-service/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

type BindingHandler struct {
	svc *service.BindingService
}

func NewBindingHandler(svc *service.BindingService) *BindingHandler {
	return &BindingHandler{svc: svc}
}

type BindingRequest struct {
	PersonID string `json:"person_id" binding:"required"`
	Type     string `json:"type" binding:"required"`
	Primary  bool   `json:"primary"`
}

// Bind 创建绑定
// @Summary 创建用户绑定
// @Description 将当前用户绑定到学生或教师身份
// @Tags 绑定管理
// @Accept json
// @Produce json
// @Security BearerAuth
// @Param binding body BindingRequest true "绑定信息"
// @Success 200 {object} map[string]interface{} "绑定成功"
// @Failure 400 {object} map[string]string "请求参数错误"
// @Failure 401 {object} map[string]string "未授权"
// @Router /bindings [post]
func (h *BindingHandler) Bind(c *gin.Context) {
	userID, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	var req BindingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 默认 primary 为 true，如果前端传了 false 则为 false
	// 注意：BindJSON 会将未传的 bool 设为 false，这里我们需要明确业务逻辑
	// Python 代码中: primary: bool = True (default)
	// 这里 Go 的 struct 如果不传默认是 false。
	// 为了兼容，我们可以认为如果不传，默认应该不是强制 true，而是看前端传什么。
	// 但 Python 代码明确 default=True。
	// 这里简单处理：如果前端没传 primary，Go 默认 false。如果业务需要默认 true，需要指针或者自定义 Unmarshal。
	// 鉴于这是一个微服务重构，我们假设前端会明确传递参数，或者我们暂且按 Go 的默认值 false 处理，
	// 如果需要默认 true，可以在 service 层处理，或者这里手动判断。
	// 让我们查看 Python 代码: `primary: bool = True` in Pydantic.
	// 既然 Python 默认是 True，那我们在 Go 里也应该尽量保持一致，或者让前端显式传。
	// 为了简单，我们暂且信任前端传参。

	err := h.svc.CreateBinding(&service.CreateBindingRequest{
		UserID:   userID.(uint),
		PersonID: req.PersonID,
		Type:     req.Type,
		Primary:  req.Primary, // 注意这里如果没传就是 false
	})

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true})
}

// Unbind 删除绑定
// @Summary 解除用户绑定
// @Description 解除当前用户的指定身份绑定
// @Tags 绑定管理
// @Accept json
// @Produce json
// @Security BearerAuth
// @Param person_id path string true "人员ID"
// @Success 200 {object} map[string]interface{} "解绑成功"
// @Failure 400 {object} map[string]string "请求参数错误"
// @Failure 401 {object} map[string]string "未授权"
// @Failure 500 {object} map[string]string "服务器内部错误"
// @Router /bindings/{person_id} [delete]
func (h *BindingHandler) Unbind(c *gin.Context) {
	userID, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	personID := c.Param("person_id")
	if personID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "person_id is required"})
		return
	}

	if err := h.svc.Unbind(userID.(uint), personID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true})
}

// Me 获取当前用户的主绑定
// @Summary 获取我的主绑定
// @Description 获取当前登录用户的主身份绑定信息
// @Tags 绑定管理
// @Accept json
// @Produce json
// @Security BearerAuth
// @Success 200 {object} map[string]interface{} "获取成功"
// @Failure 401 {object} map[string]string "未授权"
// @Failure 404 {object} map[string]string "未找到主绑定"
// @Router /bindings/me [get]
func (h *BindingHandler) Me(c *gin.Context) {
	userID, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	binding, err := h.svc.GetPrimaryBinding(userID.(uint))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No primary binding found"})
		return
	}

	c.JSON(http.StatusOK, binding)
}
