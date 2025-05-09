from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from ..serializers.compra_insumo import CompraInsumoSerializer
from ..models.compra_insumo import CompraInsumo
from ..models.compra import Compra
from insumo.models import Insumo

class CompraInsumoViewSet(viewsets.ModelViewSet):
    queryset = CompraInsumo.objects.all()
    serializer_class = CompraInsumoSerializer

    def get_queryset(self):
        compra_id = self.request.query_params.get('compra_id')
        if compra_id:
            return CompraInsumo.objects.filter(compra_id=compra_id)
        return CompraInsumo.objects.all()

    @action(detail=False, methods=['post'], url_path='batch')
    def create_batch(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Se esperaba una lista de objetos"}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        errors = []
        compra_insumos_agrupados = {} 

        with transaction.atomic():
            for entry in data:
                try:
                    # Calcular subtotal si no viene incluido
                    if 'cantidad' in entry and 'precioUnitario' in entry and 'subtotal' not in entry:
                        entry['subtotal'] = entry['cantidad'] * entry['precioUnitario']

                    serializer = self.get_serializer(data=entry)
                    if serializer.is_valid():
                        compra_insumo = serializer.save()

                        compra = compra_insumo.compra_id

                        # Agrupar los compra_insumos por compra
                        if compra.id not in compra_insumos_agrupados:
                            compra_insumos_agrupados[compra.id] = {
                                "compra": compra,
                                "insumos": []
                            }

                        compra_insumos_agrupados[compra.id]["insumos"].append({
                            "nombre": compra_insumo.insumo_id.nombre,
                            "cantidad": compra_insumo.cantidad,
                            "precioUnitario": compra_insumo.precioUnitario,
                            "subtotal": compra_insumo.subtotal
                        })

                        created_items.append(serializer.data)
                    else:
                        errors.append(serializer.errors)
                        transaction.set_rollback(True)
                        break
                except Insumo.DoesNotExist:
                    errors.append({"error": f"El insumo con ID {entry.get('insumo_id')} no existe"})
                    transaction.set_rollback(True)
                    break
                except Compra.DoesNotExist:
                    errors.append({"error": f"La compra con ID {entry.get('compra_id')} no existe"})
                    transaction.set_rollback(True)
                    break
                except Exception as e:
                    errors.append({"error": str(e)})
                    transaction.set_rollback(True)
                    break

        if errors:
            return Response({"created": created_items, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"created": created_items}, status=status.HTTP_201_CREATED)