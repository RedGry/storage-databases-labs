package ru.iuribabalin.deliveryservice.domain;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * @author Iurii Babalin (ueretz)
 */
public interface DeliveryRepo extends JpaRepository<Delivery, String> {
}
