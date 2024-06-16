package ru.iuribabalin.deliveryservice.model;

import java.util.List;

import lombok.Getter;
import lombok.Setter;

/**
 * @author Iurii Babalin (ueretz)
 */
@Getter
@Setter
public class DeliverymanWithDeliveryDto extends DeliverymanDto {
    private List<DeliveryDto> delivery;

    public DeliverymanWithDeliveryDto(String id, String name, List<DeliveryDto> delivery) {
        super(id, name);
        this.delivery = delivery;
    }
}
