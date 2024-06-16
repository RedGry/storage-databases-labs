package ru.iuribabalin.deliveryservice.model;

import java.time.LocalDateTime;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * @author Iurii Babalin (ueretz)
 */
@Data
@AllArgsConstructor
public class DeliveryDto {
    private String orderId;
    private LocalDateTime orderDateCreated;
    private String deliveryId;
    private String deliverymanId;
    private String deliveryAddress;
    private LocalDateTime deliveryTime;
    private Integer rating;
    private Long tips;
}
