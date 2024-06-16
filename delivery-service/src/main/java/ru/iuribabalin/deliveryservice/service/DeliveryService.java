package ru.iuribabalin.deliveryservice.service;

import java.util.List;
import java.util.Locale;
import java.util.Random;

import lombok.AllArgsConstructor;
import net.datafaker.Faker;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;
import ru.iuribabalin.deliveryservice.domain.Delivery;
import ru.iuribabalin.deliveryservice.domain.DeliveryRepo;
import ru.iuribabalin.deliveryservice.domain.Deliveryman;
import ru.iuribabalin.deliveryservice.domain.DeliverymanRepo;
import ru.iuribabalin.deliveryservice.model.CreateDelivery;
import ru.iuribabalin.deliveryservice.model.DeliveryDto;
import ru.iuribabalin.deliveryservice.model.DeliverymanDto;
import ru.iuribabalin.deliveryservice.model.DeliverymanWithDeliveryDto;

/**
 * @author Iurii Babalin (ueretz)
 */
@Service
@AllArgsConstructor
public class DeliveryService {

    private final DeliveryRepo deliveryRepo;
    private final DeliverymanRepo deliverymanRepo;

    public List<DeliverymanDto> getDeliverers(Long limit, Long page) {
        Pageable pageable = PageRequest.of(
                ObjectUtils.isEmpty(page) ? 0 : page.intValue(),
                ObjectUtils.isEmpty(limit) ? 5 : limit.intValue()
        );
        return deliverymanRepo.findAll(pageable)
                .map(deliveryman -> new DeliverymanDto(deliveryman.getId(), deliveryman.getName())).toList();
    }

    public DeliverymanWithDeliveryDto getDeliveryman(String id) {
        Deliveryman deliveryman = deliverymanRepo.getReferenceById(id);
        return new DeliverymanWithDeliveryDto(deliveryman.getId(), deliveryman.getName(),
                deliveryman.getDeliveryList().stream()
                        .map(delivery -> new DeliveryDto(
                                delivery.getOrderId(),
                                delivery.getOrderDateCreated(),
                                delivery.getId(),
                                delivery.getDeliveryman().getId(),
                                delivery.getDeliveryAddress(),
                                delivery.getDeliveryTime(),
                                delivery.getRating(),
                                delivery.getTips()
                        )).toList());
    }

    public List<DeliveryDto> getDeliveryForDeliveryman(String id) {
        Deliveryman deliveryman = deliverymanRepo.getReferenceById(id);
        return deliveryman.getDeliveryList().stream()
                .map(delivery -> new DeliveryDto(
                        delivery.getOrderId(),
                        delivery.getOrderDateCreated(),
                        delivery.getId(),
                        delivery.getDeliveryman().getId(),
                        delivery.getDeliveryAddress(),
                        delivery.getDeliveryTime(),
                        delivery.getRating(),
                        delivery.getTips()
                )).toList();
    }

    public DeliveryDto createDeliveryForDeliveryman(CreateDelivery createDelivery) {
        Deliveryman deliveryman = deliverymanRepo.getReferenceById(createDelivery.getDeliverymanId());
        Delivery delivery = deliveryRepo.save(createDelivery(createDelivery, deliveryman));
        return new DeliveryDto(
                delivery.getOrderId(),
                delivery.getOrderDateCreated(),
                delivery.getId(),
                delivery.getDeliveryman().getId(),
                delivery.getDeliveryAddress(),
                delivery.getDeliveryTime(),
                delivery.getRating(),
                delivery.getTips()
        );
    }

    private Delivery createDelivery(CreateDelivery createDelivery, Deliveryman deliveryman) {
        Faker faker = new Faker(new Locale("ru"));
        return new Delivery(
                ObjectIdGenerator.generate(),
                deliveryman,
                createDelivery.getOrderId(),
                createDelivery.getOrderDateCreated(),
                faker.address().fullAddress(),
                createDelivery.getOrderDateCreated().plusMonths(randInt(30, 120)),
                randInt(1, 5),
                (long) randInt(0, 1000)
        );
    }

    private int randInt(int min, int max) {
        return new Random().nextInt((max - min) + 1) + min;
    }
}
