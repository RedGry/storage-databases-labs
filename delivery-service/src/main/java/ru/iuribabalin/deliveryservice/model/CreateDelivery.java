package ru.iuribabalin.deliveryservice.model;

import java.time.LocalDateTime;

import lombok.Data;

/**
 * @author Iurii Babalin (ueretz)
 */
@Data
public class CreateDelivery {
    private String deliverymanId;
    private String orderId;
    private LocalDateTime orderDateCreated;
}
